# -*- coding: utf-8 -*-
'''主要是统计总的运行时间和产品质量'''
from app import db, application
import threading
from Business.Equipments import EquipmentManager
from models import StatisticalProduction, ProductionInfo, StatisticalWorkTime,Record
from datetime import datetime, timedelta, date
from sqlalchemy import func
import time
import json

INTERVAL = 300 #统计间隔时间

def Count():
    '''暂时先统计每天的产品的生产情况和机器总的运行时间'''
    while True:
        time.sleep(INTERVAL)
        #先统计每天的产品的生产质量
        startTime = datetime.strptime(datetime.now().strftime('%Y-%m-%d'), '%Y-%m-%d')  # 去除具体的小时分秒
        delta = timedelta(days=1)
        spro = StatisticalProduction.query.filter(StatisticalProduction.date == startTime).first()
        if not spro:
            spro = StatisticalProduction(startTime, 0, 0, 0, 0, 0, 0, 0)
            spro.save()
        query = ProductionInfo.query.filter(ProductionInfo.begin_time.between(startTime, startTime + delta))

        spro.requlified = len(query.filter(ProductionInfo.result_eval == 'QUALIFIED').all())
        spro.reunqulified = len(query.filter(ProductionInfo.result_eval == 'UNQUALIFIED').all())
        spro.procunqulified = len(query.filter(ProductionInfo.process_eval == 'UNQUALIFIED').all())
        spro.procqulified = len(query.filter(ProductionInfo.process_eval == 'QUALIFIED').all())
        spro.finiProduction = len(query.filter(ProductionInfo.production_state == 'FINISHED').all())
        spro.waitingProduction = len(query.filter(ProductionInfo.production_state == 'WAITING').all())
        spro.producingProduction = len(query.filter(ProductionInfo.production_state == 'PRODUCING').all())

        spro.update()#更新产品统计到数据库

        #再统计每个设备的总的各种运行时间
        for equipment in EquipmentManager.GetInstance().GetAllEquipments():
            query = db.session.query
            total_run_time, = query(func.sum(Record.run_time)).filter(
                Record.equipment_id == equipment.unique_id).first()
            total_stop_time, = query(func.sum(Record.stop_time)).filter(
                Record.equipment_id == equipment.unique_id).first()
            total_exception_time, = query(func.sum(Record.exception_time)).filter(
                Record.equipment_id == equipment.unique_id).first()
            swt = StatisticalWorkTime.query.filter(StatisticalWorkTime.equipment_id==equipment.unique_id).first()
            if not swt:
                swt = StatisticalWorkTime(equipment.unique_id,0,0,0)
                swt.save()

            swt.total_exception_time = total_exception_time if total_exception_time else 0
            swt.total_run_time = total_run_time if total_run_time else 0
            swt.total_stop_time = total_stop_time if total_stop_time else 0

            swt.update()

def StartCount():
    t=threading.Thread(target=Count)
    t.start()

# 用于管理处理所有的产品质量的从统计数据
@application.template_global()
def getTodayEval():
    re = StatisticalProduction.query.filter(StatisticalProduction.date == date.today()).first()
    if re:
        return re
    else:
        return StatisticalProduction(date.today(),0,0,0,0,0,0,0)


@application.template_global()
def getHistoryEval():
    query = db.session.query
    re = query(func.sum(StatisticalProduction.procqulified), func.sum(StatisticalProduction.procunqulified),
               func.sum(StatisticalProduction.requlified), func.sum(StatisticalProduction.reunqulified)).first()
    if re:
        return list(re)
    else:
        return [0, 0, 0, 0]


@application.template_global()
def getHistoryProduce():
    re = StatisticalProduction.query.all()
    reslut = {}
    dates = []
    finish = []
    cancel = []
    for day in re:
        finish.append(day.finiProduction)
        cancel.append(day.waitingProduction)
        dates.append(day.date.strftime('%Y-%m-%d'))
    reslut['dates'] = dates
    reslut['finished'] = json.dumps(finish)
    reslut['canceled'] = json.dumps(cancel)
    return reslut


# 用于管理处理所有的生产效能的从统计数据
@application.template_global()
def getTodayRunTime():
    re = Record.query.filter(Record.date == date.today()).all()
    result = {}
    robot = ""
    collector = ""
    instance = EquipmentManager.GetInstance()
    for info in re:
        total = info.run_time + info.stop_time + info.exception_time
        if total == 0:
            total = 1
        collector += instance.GetEquipmentById(info.equipment_id).name + " " + "normal" + "\t" + str(100 * info.run_time / total) + "%" + "\n"
        collector += instance.GetEquipmentById(info.equipment_id).name + " " + "stop" + "\t" + str(100 * info.stop_time / total) + "%" + "\n"
        collector += instance.GetEquipmentById(info.equipment_id).name + " " + "exception" + "\t" + str(100 * info.exception_time / total) + "%" + "\n"

    result['robot'] = collector
    result['collector'] = collector
    return result


@application.template_global()
def getHistoryRunTime():
    re = StatisticalWorkTime.query.all()
    result = {}
    robot = ''
    collector = ''
    instance = EquipmentManager.GetInstance()
    for info in re:
        total = info.total_run_time + info.total_stop_time + info.total_exception_time
        if total == 0:
            total = 1
        collector += instance.GetEquipmentById(info.equipment_id).name + " " + "normal" + "\t" + str(
            100 * info.total_run_time / total) + "%" + "\n"
        collector += instance.GetEquipmentById(info.equipment_id).name + " " + "stop" + "\t" + str(
            100 * info.total_stop_time / total) + "%" + "\n"
        collector += instance.GetEquipmentById(info.equipment_id).name + " " + "exception" + "\t" + str(
            100 * info.total_exception_time / total) + "%" + "\n"

    result['robot'] = collector
    result['collector'] = collector
    return result

# 获取历史的成本消耗数据
def getHistoryCost():
    totalCost = Record.query.all()
    result = {}
    date = []
    power = []
    air = []
    welding_wrie = []
    for cost in totalCost:
        date.append(cost.date.strftime('%Y-%m-%d'))
        air.append(cost.air_consumption)
        power.append(cost.power_consumption)
        welding_wrie.append(cost.welding_wire_consumption)
    result['air'] = air
    result['date'] = date
    result['power'] = power
    result['weldingwire'] = welding_wrie
    return result