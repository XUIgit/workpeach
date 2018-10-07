# -*- coding:utf-8 -*-
from app import application
from flask import url_for, render_template, request, redirect
import json
from datamodels import CollectionDatas,CollectionDataSeria
from models import RobotInfo, AgvPos
import datetime
import time

from Business import EquipmentManager


@application.route('/ma_workshorp/overview/<int:factoryId>')
def ma_workshop_overview(factoryId):
    if not factoryId:
        factoryId = 1
    robotModels = RobotInfo.query.filter_by(factoryId=factoryId).all()
    return render_template('manage/workshopoverview.html', titlename='车间视图', robotModels=robotModels)


@application.route('/ma_workshop/dataview/<equipment_id>')
def ma_workshop_dataview(equipment_id):
    #查询最近1000条作为初始数据
    data = CollectionDatas.query.filter_by(equipment_id=equipment_id).limit(1000).all()
    vdatas = []
    edatas = []
    tdatas = []
    for col in data[::-1]:
        edatas.append([time.mktime(col.time.timetuple()) * 1000, col.electricity])
        vdatas.append([time.mktime(col.time.timetuple()) * 1000, col.voltage])
        tdatas.append([time.mktime(col.time.timetuple()) * 1000, col.temperature])
    data = dict()
    data['e'] = edatas
    data['v'] = vdatas
    data['t'] = tdatas
    return render_template('manage/workshopdataview.html', titlename='数据视图', equipment_id=equipment_id, thousandData=data)


@application.route('/ma_workshop/getCollectedDatas/<equipment_id>')
def ma_workshop_getCollectedDatas(equipment_id):
    # devid是一个16位的标识符 不是在config的id
    data = None
    data = CollectionDatas.query.filter_by(equipment_id=equipment_id).first()
    equipment = EquipmentManager.GetInstance().GetEquipmentById(equipment_id)
    if not data:
        data = CollectionDatas(equipment_id,
                               None,
                               0, 0, 0, equipment.status)
    return json.dumps(data, default=CollectionDataSeria)


@application.route('/ma_workshop/getRobotModels', methods=['GET', 'POST'])
def ma_workshop_getRobotModels():
    if request.method == 'POST':
        data = json.loads(request.data)
        factoryId = data["factoryId"]
    if not factoryId:
        factoryId = 1
    robotModels = RobotInfo.query.filter_by(factoryId=factoryId).all()
    result = dict()
    for info in robotModels:
        tmp = dict()
        tmp["uniqueid"] = info.uniqueid
        tmp["posX"] = info.posX
        tmp["posY"] = info.posY
        tmp["width"] = info.width
        tmp["height"] = info.height
        tmp["factoryId"] = info.factoryId
        tmp["imageURL"] = info.imageURL
        result[info.uniqueid] = tmp
    return json.dumps(result)


@application.route('/ma_workshop/getAgvPos', methods=['GET'])
def ma_workshop_getAgvPose():
    re = AgvPos.query.first()
    result = []
    if re:
        result.append(re.pos_X)
        result.append(re.pos_Y)
        result.append(0)
        result.append(0)
    return json.dumps(result)


@application.route('/ma_workshop/searchHistoryDatas', methods=['POST'])
def ma_workshop_searchHistoryDatas():
    if request.form['startTime'] and request.form['production_id']:
        reTime = {}
        reTime['startTime'] = request.form['startTime']
        reTime['endTime'] = request.form['endTime']
        id = int(request.form['production_id'])
        query = CollectionDatas.query.filter_by(equipment_id = id)
        startTime = datetime.datetime.strptime(reTime['startTime'], '%Y-%m-%d %H:%M:%S')
        if reTime['endTime']:
            data = query.filter(CollectionDatas.time.between(startTime, datetime.datetime.strptime(reTime['endTime'],
                                                                                          '%Y-%m-%d %H:%M:%S'))).all()
        else:
            reTime['endTime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data = query.filter(CollectionDatas.time.between(startTime,
                                                            datetime.datetime.now())).all()
        vdatas = []
        edatas = []
        tdatas = []
        for col in data[::-1]:
            vdatas.append([time.mktime(col.time.timetuple()) * 1000, col.voltage])
            edatas.append([time.mktime(col.time.timetuple()) * 1000, col.electricity])
            tdatas.append([time.mktime(col.time.timetuple()) * 1000, col.temperature])
        data = dict()
        data['v'] = vdatas
        data['e'] = edatas
        data['t'] = tdatas
    else:
        return redirect(url_for('ma_index_index'))
    return render_template('manage/workshopdataview.html', titlename='历史采集数据', reTime=reTime, thousandData=data, id=id)
