from app import db
from models import EquipmentModel

'''
通过EquipmentManager.Getinstance() 从数据库中初始化相应的实例 通过GetAllColletcors等获取初始完成的设备list
修改过的设备对象通过save方法同步到数据库修改
尽量通过EquipemtFactory产生新的设备对象 然后通过save方法新增到数据库
或者直接通过EquipmentManager.AddEquipment(ip,port,....) （该函数返回相应的对象实例）直接添加到数据库，也会更新manager返回的对象list
'''

class Equipment:
    '''设备的基类'''

    def __init__(self,sql_model, exist_in_db=True):
        self.__sql_model = sql_model
        self.__exist_in_db = exist_in_db

    def save(self):
        if self.__exist_in_db:#存在于数据库中直接提交更新
            db.session.commit()
        else:#不存在则先添加
            db.session.add(self.__sql_model)
            db.session.commit()
            self.__exist_in_db = True

    @property
    def id(self):
        return self.__sql_model.id

    @property
    def exist_status(self):
        return self.__sql_model.exist_status

    @exist_status.setter
    def exist_status(self, value):
        if type(value) == str:
            self.__sql_model.exist_status = value
        else:
            raise ValueError("exist_status's type is str")

    @property
    def unique_id(self):
        return self.__sql_model.unique_id

    @property
    def type(self):
        return self.__sql_model.type

    @type.setter
    def type(self, value):
        if type(value) == str:
            self.__sql_model.type = value
        else:
            raise ValueError("type's type is str")

    @property
    def name(self):
        return self.__sql_model.name

    @name.setter
    def name(self, value):
        if type(value) == str:
            self.__sql_model.name = value
        else:
            raise ValueError("name's type is str")

    @property
    def son_equipment_id(self):
        return self.__sql_model.son_equipment_id

    @son_equipment_id.setter
    def son_equipment_id(self, value):
        if type(value) == str:
            self.__sql_model.son_equipment_id = value
        else:
            raise ValueError("son_equipment_id's type is str")
    @property
    def ip(self):
        return self.__sql_model.ip
    @ip.setter
    def ip(self, value):
        if type(value) == str:
            self.__sql_model.ip = value
        else:
            raise ValueError("ip's type is str")
    @property
    def port(self):
        return self.__sql_model.port
    @port.setter
    def port(self, value):
        if type(value) == int:
            self.__sql_model.port = value
        else:
            raise ValueError("port's type is int")

    def run(self):
        pass

class WeldingEquipment(Equipment):
    '''焊接设备的基类'''

    def GetCollector(self):
        if not self.__collector:
            #第一次调用此函数
            for collector in EquipmentManager.GetInstance().GetAllCollectors():
                if collector.unique_id == self.son_equipment_id:
                    self.__collector = collector
                    return collector
        else:
            return self.__collector

    def __init__(self, sql_model, exist_in_db=True):
        Equipment.__init__(sql_model, exist_in_db)
        #其连接的采集器
        self.__collector = None

    def run(self):
        pass


class Robot(Equipment):

    '''焊接设备的基类'''

    def __init__(self, sql_model, exist_in_db=True):
        Equipment.__init__(self, sql_model, exist_in_db)
        pass

    def run(self):
        pass


class Collector(Equipment):
    '''采集器'''

    def __init__(self, sql_model, exist_in_db=True):
        Equipment.__init__(self, sql_model, exist_in_db)
        pass

    def run(self):
        pass


class WeldingGun(WeldingEquipment):
    '''焊枪'''

    def __init__(self, sql_model, exist_in_db=True):
        WeldingEquipment.__init__(self, sql_model, exist_in_db)
        pass

    def run(self):
        pass


class CuttingMachine(WeldingEquipment):
    '''切割机'''

    def __init__(self, sql_model, exist_in_db=True):
        WeldingEquipment.__init__(self, sql_model, exist_in_db)
        pass

    def run(self):
        pass


class EquipmentFactory:

    types = ['collector','robot', 'weldinggun','cuttingmachine']

    @staticmethod
    def GetAllEquipments(type):
        '''从数据库得到所有的type类型的设备对象list'''
        if not type in EquipmentFactory.types:
            raise ValueError("type not found")
        re = []
        equipments = EquipmentModel.query.filter_by(type=type)
        for equipment in equipments:
            eq = eval(type.capitalize()+"(equipment)")
            re.append(eq)
        return re

    @staticmethod
    def CreateEquipment(type):
        '''创建Equipement对象'''
        if not type in EquipmentFactory.types:
            raise ValueError("type not found")
        else:
            sql_model = EquipmentModel(type=type)
            return eval(type.capitalize()+"(sql_model,False)")

class EquipmentManager:
    '''单列模式'''
    __instance = None

    def __new__(cls, *args, **kwargs):
        return EquipmentManager.GetInstance()

    @staticmethod
    def GetInstance():
        if not EquipmentManager.__instance:
            '''执行初始化'''
            EquipmentManager.__instance = object.__new__(EquipmentManager)
            # 查询数据库 实例化各个设备
            EquipmentManager.__instance.__collectors = EquipmentFactory.GetAllEquipments("collector")
            EquipmentManager.__instance.__robots = EquipmentFactory.GetAllEquipments("robot")
            EquipmentManager.__instance.__cuttingmachines = EquipmentFactory.GetAllEquipments("cuttingmachine")
            EquipmentManager.__instance.__weldingguns = EquipmentFactory.GetAllEquipments("weldinggun")

        return EquipmentManager.__instance

    #添加新设备并返回对象
    def AddEquipment(self, type, ip, port, name, exist_status=None, son_equipment_id=None):
        e = EquipmentFactory.CreateEquipment(type)
        e.ip = ip
        e.port = port
        e.name = name
        e.exist_status = exist_status
        e.son_equipment_id = son_equipment_id
        e.save()
        if type == 'collector':
            self.__collectors.append(e)
        elif type == 'robot':
            self.__robots.append(e)
        elif type == 'cuttingmachine':
            self.__cuttingmachines.append(e)
        elif type == 'weldinggun':
            self.__weldingguns.append(e)
        return e

    def GetAllCollectors(self):
        return self.__collectors

    def GetAllRobots(self):
        return self.__robots

    def GetAllWeldingGun(self):
        return self.__cuttingmachines

    def GetAllCuttingMachine(self):
        return self.__weldingguns