from models import EquipmentModel

class Equipment:
    '''设备的基类'''

    def __init__(self,sql_model):
        self.__sql_model = sql_model

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
            self.__sql_model.commit()
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
            self.__sql_model.commit()
        else:
            raise ValueError("type's type is str")

    @property
    def name(self):
        return self.__sql_model.name

    @name.setter
    def name(self, value):
        if type(value) == str:
            self.__sql_model.name = value
            self.__sql_model.commit()
        else:
            raise ValueError("name's type is str")

    def run(self):
        pass

class WeldingEquipment(Equipment):
    '''焊接设备的基类'''

    def __init__(self, sql_model):
        Equipment.__init__(sql_model)
        pass

    def run(self):
        pass


class Robot(Equipment):

    '''焊接设备的基类'''

    def __init__(self, sql_model):
        Equipment.__init__(self, sql_model)
        pass

    def run(self):
        pass


class Collector(Equipment):
    '''采集器'''

    def __init__(self, sql_model):
        Equipment.__init__(self, sql_model)
        pass

    def run(self):
        pass


class WeldingGun(WeldingEquipment):
    '''焊枪'''

    def __init__(self, sql_model):
        WeldingEquipment.__init__(self, sql_model)
        pass

    def run(self):
        pass


class CuttingMachine(WeldingEquipment):
    '''切割机'''

    def __init__(self, sql_model):
        WeldingEquipment.__init__(self, sql_model)
        pass

    def run(self):
        pass


class EquipmentFactory:

    types = ['collector','robot', 'weldinggun','cuttingmachine']

    @staticmethod
    def GetEquipment(type):
        if not type in EquipmentFactory.types:
            raise ValueError("type not found")
        re = []
        equipments = EquipmentModel.query().filter_by(type=type)
        for equipment in equipments:
            eq = eval(type.capitalize()+"(equipment)")
            re.append(eq)
        return re



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
            EquipmentManager.__instance.collectors = EquipmentFactory.GetEquipment("collector")
            EquipmentManager.__instance.robots = EquipmentFactory.GetEquipment("robot")
            EquipmentManager.__instance.cuttingmachines = EquipmentFactory.GetEquipment("cuttingmachine")
            EquipmentManager.__instance.weldingguns = EquipmentFactory.GetEquipment("weldinggun")
        return EquipmentManager.__instance

    def GetAllCollectors(self):
        return self.collectors

    def GetAllRobots(self):
        return self.robots

    def GetAllWeldingGun(self):
        return self.cuttingmachines

    def GetAllCuttingMachine(self):
        return self.weldingguns