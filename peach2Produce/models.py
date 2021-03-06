# -*- coding: utf-8 -*-
from app import db, application
from utils import randomStr, encrypt, decrypt
from flask import session
from sqlalchemy import and_, desc, func
import time

import datetime
import json


# User类 用于登录的模型
class Users(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(320), unique=True)
    password = db.Column(db.Binary(32), nullable=False)
    key = db.Column(db.String(32), nullable=False, unique=True)

    def __init__(self, username, password, email):
        self.key = randomStr(32)  # 32位随机字符 唯一标识用户
        self.username = str(username)
        self.email = email
        self.password = encrypt(password)

    # 登录函数 在数据库中验证
    @staticmethod
    def login(username, password):
        # 先查询用户名
        re = Users.query.filter_by(username=username).first()
        # 没查到则查email
        if not re:
            re = Users.query.filter_by(email=username).first()

        if re and re.isRight(password):
            #cookie保存在浏览器
            session['username_key'] = re.key
            session['password'] = re.password
            session.permanent = True
            return True
        else:
            return False

    # 存入数据库
    def save(self):
        if self.validate():
            db.session.add(self)
            db.session.commit()
            return True
        else:
            return False

    # 验证用户输入是否正确
    def validate(self):
        return True

    def __repr__(self):
        return "Username: %s" % self.username

    # 参数password 明文或密文
    def isRight(self, password, isplain=True):
        if isplain:
            if decrypt(self.password) == password:
                return True
            else:
                return False
        else:
            if self.password == password:
                return True
            else:
                return False


# 用于处理本地主机配置的模型
class LocalHostConfig(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    host_id = db.Column(db.String(16), unique=True)
    upload_interval = db.Column(db.Integer, unique=False)

    def __init__(self, host_id, upload_interval):
        self.host_id = host_id
        self.upload_interval = upload_interval

    @staticmethod
    def load(request):
        host_id = request.form.get('localHostId')
        interval = request.form.get('localHostInterval')
        l = LocalHostConfig.query.first()
        l.host_id = host_id
        l.upload_interval = interval
        return l

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()


# 用于处理远程主机配置的模型
class RemoteHostConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.String(200), unique=True)

    def __init__(self, url):
        self.url = url

    @staticmethod
    def load(request):
        url = request.form.get('remoteHostUrl')
        r = RemoteHostConfig.query.first()
        r.url = url
        return r

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()


# 用于生产信息查询form的模型
class SearchInfoForm:
    def __init__(self, productId, techId, status, processEval, resultEval):
        self.productId = productId
        self.status = status
        self.processEval = processEval
        self.resultEval = resultEval
        self.techId = techId

    @staticmethod
    def load(request):
        if 'productId' in request.form:
            return SearchInfoForm(request.form['productId'],
                                  request.form['techId'],
                                  request.form['status'],
                                  request.form['processEval'],
                                  request.form['resultEval'])
        else:
            return SearchInfoForm('',
                                  '',
                                  '',
                                  '',
                                  '',
                                  )

    def getSearchResults(self):
        return ProductControlInfo.search(self)


# 用于生产信息查询form的模型
class SearchTechniqueInfoForm:
    def __init__(self, productKind, robotId, techniqueId):
        self.productKind = productKind
        self.robotId = robotId  # config里的临时id
        self.techniqueId = techniqueId

    @staticmethod
    def load(request):
        if 'productKind' in request.form:
            return SearchTechniqueInfoForm(request.form['productKind'] if request.form['productKind'] else '',
                                           request.form['robotId'] if request.form['robotId'] else '',
                                           request.form['techniqueId'] if request.form['techniqueId'] else '',
                                           )
        else:
            return SearchTechniqueInfoForm('',
                                           '',
                                           ''
                                           )

    def getSearchResults(self):
        return TechniqueInfo.search(self)


# 生产产品生产模型
class ProductControlInfo(db.Model):
    __mapper_args__ = {
        "order_by": desc('beginTime')
    }
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    productId = db.Column(db.String(32), unique=False, nullable=False)
    techId = db.Column(db.String(32), unique=False, nullable=False)
    status = db.Column(db.String(32), nullable=False)
    processEval = db.Column(db.String(32), nullable=False, unique=False)
    resultEval = db.Column(db.String(32), nullable=False, unique=False)
    desc = db.Column(db.String(100), nullable=True, unique=False)
    beginTime = db.Column(db.DateTime, unique=False, default=datetime.datetime.now())
    endTime = db.Column(db.DateTime, unique=False, default=datetime.datetime.now())

    def __init__(self, productId, techId, status, processEval, resultEval, desc, beginTime, endTime):
        self.productId = productId
        self.techId = techId
        self.status = status
        self.processEval = processEval
        self.resultEval = resultEval
        self.desc = desc
        self.beginTime = beginTime
        self.endTime = endTime

    def save(self):
        db.session.add(self)
        db.session.commit()

    def commit(self):
        db.session.commit()

    @staticmethod
    def search(infoForm):
        filter = []
        if infoForm.productId:
            filter.append(ProductControlInfo.productId == infoForm.productId)
        if infoForm.techId:
            filter.append(ProductControlInfo.techId == infoForm.techId)
        if infoForm.status:
            filter.append(ProductControlInfo.status == infoForm.status)
        if infoForm.processEval:
            filter.append(ProductControlInfo.processEval == infoForm.processEval)
        if infoForm.resultEval:
            filter.append(ProductControlInfo.resultEval == infoForm.resultEval)

        return ProductControlInfo.query.filter(and_(*filter)).limit(100).all()  # 一次性最多产生100条


# 生产产品样本
class ProductInfo(db.Model):
    ID = db.Column(db.String(255), primary_key=True, unique=False, nullable=False)
    Product_name = db.Column(db.String(255), unique=False, nullable=False)
    Product_code = db.Column(db.String(255), nullable=False)
    Industry = db.Column(db.String(255), nullable=False, unique=False)
    Drawing_url = db.Column(db.String(255), nullable=False, unique=False)
    Weld_number = db.Column(db.String(255), nullable=True, unique=False)
    Weld_position = db.Column(db.String(255), nullable=True, unique=False)
    Joint_type = db.Column(db.String(255), nullable=True, unique=False)
    Cross_section_type_size = db.Column(db.String(255), nullable=True, unique=False)
    Length_of_weld = db.Column(db.String(255), nullable=True, unique=False)
    Welding_quality_grade = db.Column(db.String(255), nullable=True, unique=False)
    Welding_quality_grade_remark = db.Column(db.String(255), nullable=True, unique=False)
    Weld_performance_level = db.Column(db.String(255), nullable=True, unique=False)
    Weld_performance_level_remark = db.Column(db.String(255), nullable=True, unique=False)
    Stress_grade = db.Column(db.String(255), nullable=True, unique=False)
    Safety_grade = db.Column(db.String(255), nullable=True, unique=False)
    Imperfection_quality_level = db.Column(db.String(255), nullable=True, unique=False)
    Imperfection_quality_level_remark = db.Column(db.String(255), nullable=True, unique=False)
    Weld_inspection_level = db.Column(db.String(255), nullable=True, unique=False)
    Weld_inspection_level_remark = db.Column(db.String(255), nullable=True, unique=False)
    Volumetric_tests = db.Column(db.String(255), nullable=True, unique=False)
    Surface_tests = db.Column(db.String(255), nullable=True, unique=False)
    Visual_examination = db.Column(db.String(255), nullable=True, unique=False)
    Weld_length_tolerance = db.Column(db.String(255), nullable=True, unique=False)
    Weld_length_tolerance_remark = db.Column(db.String(255), nullable=True, unique=False)
    Weld_shape_tolerance = db.Column(db.String(255), nullable=True, unique=False)
    Weld_shape_tolerance_remark = db.Column(db.String(255), nullable=True, unique=False)
    Weld_tolerance = db.Column(db.String(255), nullable=True, unique=False)
    Weld_tolerance_remark = db.Column(db.String(255), nullable=True, unique=False)
    Weld_method = db.Column(db.String(255), nullable=True, unique=False)

    def __init__(self, ID, Product_name, Product_code, Industry, Drawing_url, Weld_number, Weld_position, Joint_type
                 , Cross_section_type_size, Length_of_weld, Welding_quality_grade, Welding_quality_grade_remark,
                 Weld_performance_level, Weld_performance_level_remark, Stress_grade, Safety_grade,
                 Imperfection_quality_level,
                 Imperfection_quality_level_remark, Weld_inspection_level, Weld_inspection_level_remark,
                 Volumetric_tests, Surface_tests,
                 Visual_examination, Weld_length_tolerance, Weld_length_tolerance_remark, Weld_shape_tolerance,
                 Weld_shape_tolerance_remark, Weld_tolerance, Weld_tolerance_remark, Weld_method):

        self.ID = ID
        self.Product_name = Product_name
        self.Product_code = Product_code
        self.Industry = Industry
        self.Drawing_url = Drawing_url
        self.Weld_number = Weld_number
        self.Weld_position = Weld_position
        self.Joint_type = Joint_type
        self.Cross_section_type_size = Cross_section_type_size
        self.Length_of_weld = Length_of_weld
        self.Welding_quality_grade = Welding_quality_grade
        self.Welding_quality_grade_remark = Welding_quality_grade_remark
        self.Weld_performance_level = Weld_performance_level
        self.Weld_performance_level_remark = Weld_performance_level_remark
        self.Stress_grade = Stress_grade
        self.Safety_grade = Safety_grade
        self.Imperfection_quality_level = Imperfection_quality_level
        self.Imperfection_quality_level_remark = Imperfection_quality_level_remark
        self.Weld_inspection_level = Weld_inspection_level
        self.Weld_inspection_level_remark = Weld_inspection_level_remark
        self.Volumetric_tests = Volumetric_tests
        self.Surface_tests = Surface_tests
        self.Visual_examination = Visual_examination
        self.Weld_length_tolerance = Weld_length_tolerance
        self.Weld_length_tolerance_remark = Weld_length_tolerance_remark
        self.Weld_shape_tolerance = Weld_shape_tolerance
        self.Weld_shape_tolerance_remark = Weld_shape_tolerance_remark
        self.Weld_tolerance = Weld_tolerance
        self.Weld_tolerance_remark = Weld_tolerance_remark
        self.Weld_method = Weld_method

    def save(self):
        db.session.add(self)
        db.session.commit()

    def commit(self):
        db.session.commit()

    @staticmethod
    def search(infoForm):
        filter = []
        if infoForm.productId:
            filter.append(ProductInfo.productId == infoForm.productId)
        if infoForm.techId:
            filter.append(ProductInfo.techId == infoForm.techId)
        if infoForm.status:
            filter.append(ProductInfo.status == infoForm.status)
        if infoForm.processEval:
            filter.append(ProductInfo.processEval == infoForm.processEval)
        if infoForm.resultEval:
            filter.append(ProductInfo.resultEval == infoForm.resultEval)

        return ProductInfo.query.filter(and_(*filter)).limit(100).all()  # 一次性最多产生100条


# 生产产品模型
class TechniqueInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    techniqueId = db.Column(db.String(16), unique=False, nullable=False)
    productKind = db.Column(db.String(16), unique=False, nullable=False)
    robotId = db.Column(db.String(16), unique=False, nullable=False)
    electricity = db.Column(db.Float, unique=False, nullable=True)
    voltage = db.Column(db.Float, unique=False, nullable=True)
    temperature = db.Column(db.Float, unique=False, nullable=True)

    def __init__(self, techniqueId, productKind, robotId, electricity, voltage, temperature):
        self.techniqueId = techniqueId
        self.productKind = productKind
        self.robotId = robotId
        self.electricity = electricity
        self.voltage = voltage
        self.temperature = temperature

    def save(self):
        db.session.add(self)
        db.session.commit()

    def commit(self):
        db.session.commit()

    @staticmethod
    def search(infoForm):
        filter = []
        if infoForm.productKind:
            filter.append(TechniqueInfo.productKind == infoForm.productKind)
        if infoForm.techniqueId:
            filter.append(TechniqueInfo.techniqueId == infoForm.techniqueId)
        if infoForm.robotId:
            filter.append(TechniqueInfo.robotId == infoForm.robotId)

        return TechniqueInfo.query.filter(and_(*filter)).limit(100).all()  # 一次性最多产生100条


# 用于统计历史数据的表 ，每条记录是每一天的，通过对一列求和得到总和
class StatisticalProduction(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    finiProduction = db.Column(db.Integer, nullable=False)
    waitingProduction = db.Column(db.Integer, nullable=False)
    producingProduction = db.Column(db.Integer, nullable=False)
    procqulified = db.Column(db.Integer, nullable=False)
    procunqulified = db.Column(db.Integer, nullable=False)
    requlified = db.Column(db.Integer, nullable=False)
    reunqulified = db.Column(db.Integer, nullable=False)

    def __init__(self, date, finiProduction, waitingProduction, producingProduction, procqulified, procunqulified, requlified, reunqulified):
        self.date = date
        self.finiProduction = finiProduction
        self.waitingProduction = waitingProduction
        self.producingProduction = producingProduction
        self.procqulified = procqulified
        self.procunqulified = procunqulified
        self.requlified = requlified
        self.reunqulified = reunqulified

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()


class StatisticalWorkTime(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    equipment_id = db.Column(db.String(16), unique=False)
    total_run_time = db.Column(db.Float)
    total_exception_time = db.Column(db.Float)
    total_stop_time = db.Column(db.Float)

    def __init__(self, equipment_id, total_run_time, total_exception_time, total_stop_time):
        self.equipment_id = equipment_id
        self.total_run_time = total_run_time
        self.total_exception_time = total_exception_time
        self.total_stop_time = total_stop_time

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()


# 机器人信息的表
class RobotInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uniqueid = db.Column(db.String(16), unique=True)
    type = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(60), nullable=False)
    status = db.Column(db.String(16), nullable=False)
    factoryId = db.Column(db.String(100), nullable=False)
    imageURL = db.Column(db.String(100), nullable=False)
    posX = db.Column(db.Float, nullable=False)
    posY = db.Column(db.Float, nullable=False)
    posZ = db.Column(db.Float, nullable=False)
    width = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)

    def __init__(self, type, model, status, factoryId, imageURL, posX, posY, posZ,width,height):
        self.uniqueid = randomStr(16)
        self.type = type
        self.model = model
        self.status = status
        self.factoryId = factoryId
        self.imageURL = imageURL
        self.posX = posX
        self.posY = posY
        self.posZ = posZ
        self.width = width
        self.height = height

    def save(self):
        db.session.add(self)
        db.session.commit()

    def commit(self):
        db.session.commit()

# 机器人信息的表
class FactoryInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uniqueid = db.Column(db.String(16), unique=True)
    name = db.Column(db.String(64), unique=True)
    latitude = db.Column(db.Float, unique=True)
    longitude = db.Column(db.Float, unique=True)
    robotIds = db.Column(db.String(128), unique=True)

    def __init__(self, name, latitude, longitude, factoryId, robotIds):
        self.uniqueid = randomStr(16)
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.robotIds = robotIds

    def save(self):
        db.session.add(self)
        db.session.commit()


class RobotRunInfo(db.Model):
    uniqueid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    techniqueId = db.Column(db.String(64), nullable=False)
    time = db.Column(db.DateTime, unique=False, default=datetime.datetime.now())
    run_status = db.Column(db.String(64), nullable=False)

    def __init__(self, time, techniqueId, run_status):
        self.techniqueId = techniqueId
        self.time = time
        self.run_status = run_status

    def save(self):
        db.session.add(self)
        db.session.commit()

    def commit(self):
        db.session.commit()


class InteractiveMessageInfo(db.Model):
    messageid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    flowid = db.Column(db.String(16), unique=False)
    time = db.Column(db.DateTime, unique=False, default=datetime.datetime.now())
    type = db.Column(db.String(16), unique=False)
    data = db.Column(db.String(1024), unique=False)
    sender = db.Column(db.String(16), unique=False)
    receiver = db.Column(db.String(16), unique=False)

    def __init__(self, flow_id, time, type, data, sender, receiver):
        self.flow_id = flow_id
        self.time = time
        self.type = type
        self.data = data
        self.sender = sender
        self.receiver = receiver

    def save(self):
        db.session.add(self)
        db.session.commit()

    def commit(self):
        db.session.commit()


# agv的表
class AgvPos(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pos_X = db.Column(db.Float, default=0)
    pos_Y = db.Column(db.Float, default=0)
    pos_Z = db.Column(db.Float, default=0)

    def __init__(self, x, y, z):
        self.pos_Z = z
        self.pos_Y = y
        self.pos_X = x

    def add(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()


##########################################################################################################################################################
'''重新构建的新的模型'''

# 储存设备信息表
class EquipmentInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    unique_id = db.Column(db.String(16), unique=True)
    ip = db.Column(db.String(16), unique=False, nullable=False)
    port = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(64), unique=False, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    son_equipment_id = db.Column(db.String(16), nullable=True)  # 此设备 所连接(包含)的设备

    def __init__(self, unique_id, ip=None, port=None, type=None, name=None, son_equipment_id=None):
        self.unique_id = unique_id
        self.ip = ip
        self.port = port
        self.type = type
        self.name = name
        self.son_equipment_id = son_equipment_id

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def commit(self):
        db.session.commit()

#储存产品信息的表
class ProductionInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    technology_id = db.Column(db.String(16), unique=False, nullable=False)
    production_id = db.Column(db.String(16), unique=True, nullable=False)
    production_category = db.Column(db.String(16), unique=False, nullable=False)
    equipment_id = db.Column(db.String(16), unique=False, nullable=False)
    production_state = db.Column(db.String(16), unique=False, nullable=False)
    process_eval = db.Column(db.String(16), unique=False, nullable=False)
    result_eval = db.Column(db.String(16), unique=False, nullable=False)
    begin_time = db.Column(db.DateTime, unique=False, default=datetime.datetime.now())
    end_time = db.Column(db.DateTime, unique=False, default=datetime.date(2100, 1, 1))

    def __init__(self, technology_id, production_id, production_category, equipment_id, production_state,process_eval,result_eval,begin_time,end_time):
        self.technology_id = technology_id
        self.production_id = production_id
        self.production_category = production_category
        self.production_state = production_state
        self.equipment_id = equipment_id
        self.result_eval = result_eval
        self.process_eval = process_eval
        self.begin_time = begin_time
        self.end_time = end_time

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()


class Record(db.Model):
    '''设备每天的运行时间和消耗量'''
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    equipment_id = db.Column(db.String(16), unique=False)
    run_time = db.Column(db.Float)
    stop_time = db.Column(db.Float)
    exception_time = db.Column(db.Float)
    date = db.Column(db.Date, nullable=False)
    air_consumption = db.Column(db.Float)
    welding_wire_consumption = db.Column(db.Float)
    power_consumption = db.Column(db.Float)

    def __init__(self, equipment_id, run_time, stop_time, exception_time, air_consumption, welding_wire_consumption, power_consumption):
        self.equipment_id = equipment_id
        self.run_time = run_time
        self.stop_time = stop_time
        self.exception_time = exception_time
        self.date = time.strftime('%Y-%m-%d')
        self.air_consumption = air_consumption
        self.welding_wire_consumption = welding_wire_consumption
        self.power_consumption = power_consumption

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()


class CollectionDatas(db.Model):
    __mapper_args__ = {
        "order_by": desc('time')
    }
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    electricity = db.Column(db.Float, unique=False)
    voltage = db.Column(db.Float, unique=False)
    temperature = db.Column(db.Float, unique=False)
    production_Id = db.Column(db.String(16), unique=False, nullable=True)
    equipment_id = db.Column(db.String(16), unique=False)
    time = db.Column(db.DateTime, unique=False, default=datetime.datetime.now(), onupdate=datetime.datetime.now())
    state = db.Column(db.String(16), unique=False, nullable=True)

    def __init__(self, equipment_id, production_Id, electricity, voltage, temperature, state):
        self.electricity = electricity
        self.voltage = voltage
        self.temperature = temperature

        self.production_Id = production_Id
        self.equipment_id = equipment_id
        self.time = datetime.datetime.now()
        self.state = state

    def save(self):
        db.session.add(self)
        db.session.commit()

def CollectionDataSeria(obj):
    return {
        'time': obj.time.strftime('%Y/%m/%d %H:%M:%S'),
        'e': obj.electricity,
        'v': obj.voltage,
        't': obj.temperature,
        'productId': obj.production_Id,
        'produce_status': obj.state,
    }