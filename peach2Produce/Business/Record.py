#-*- coding:utf-8 -*-
'''主要是记录设备运行时间和成本消耗'''
from Business.Equipments import EquipmentManager
from models import Record
from datamodels import CollectionDatas
from sqlalchemy import and_
import threading
import time

TIMEINTERVAL = 2 #每次循环的时间间隔
COSTINTERVAL = 2

def RecordTime():
    instance = EquipmentManager.GetInstance()
    while True:
        time.sleep(TIMEINTERVAL)
        for equipment in instance.GetAllEquipments():
            re = Record.query.filter(
                and_(Record.equipment_id == equipment.unique_id, Record.date == time.strftime('%Y-%m-%d'))).first()
            if not re:
                re = Record(equipment.unique_id, 0, 0, 0, 0, 0)
                re.save()

            if equipment.status == "running":
                re.run_time += TIMEINTERVAL
            elif equipment.status == "stop":
                re.stop_time += TIMEINTERVAL
            elif equipment.status == "exception":
                re.exception_time += TIMEINTERVAL

            re.update()

def RecordCost():
    instance = EquipmentManager.GetInstance()
    for equipment in instance.GetAllEquipments():#初始化last_cd
        equipment.last_cd = CollectionDatas.query.filter(CollectionDatas.equipment_id == equipment.unique_id).first()
        if not equipment.last_cd:
            equipment.last_cd = CollectionDatas(equipment.unique_id, '0000000', 0, 0, 0, "exception")

    while True:
        time.sleep(COSTINTERVAL)
        for equipment in instance.GetAllEquipments():
            cd = CollectionDatas.query.filter(CollectionDatas.equipment_id == equipment.unique_id).first()
            if not cd:
                continue
            AIRCONSUM = equipment.working_production.working_procedure.technology.AIRCONSUM if equipment.working_production else 0  # 每分钟耗气量(L/min)
            WELDINGWIRECONSUM = equipment.working_production.working_procedure.technology.WELDINGWIRECONSUM if equipment.working_production else 0  # 每分钟焊丝消耗量(kg/min)
            re = Record.query.filter(
                and_(Record.equipment_id == equipment.unique_id, Record.date == time.strftime('%Y-%m-%d'))).first()
            if not re:
                re = Record(equipment.unique_id, 0, 0, 0, 0, 0)
                re.save()
            re.power_consumption += (( ((cd.electricity + equipment.last_cd.electricity)/2) * ((cd.voltage + equipment.last_cd.voltage) / 2)) / 1000 * (COSTINTERVAL / 3600))
            re.air_consumption += (AIRCONSUM * (COSTINTERVAL / 60))
            re.welding_wire_consumption += (WELDINGWIRECONSUM * (COSTINTERVAL / 60)) * 1000
            equipment.last_cd = CollectionDatas.query.filter(
                CollectionDatas.equipment_id == equipment.unique_id).first()


def StartRecord():
    t_time = threading.Thread(target=RecordTime)
    t_cost = threading.Thread(target=RecordCost)

    t_cost.start()
    t_time.start()