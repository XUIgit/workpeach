from Equipments import EquipmentManager
from utils import randomStr
from models import ProductionInfo

class WorkingProcedure:
    '''工序类  工序类中包含具体工艺流程'''
    pass

class Production:
    '''生产模型 包含具体的产品信息'''
    def __init__(self, production_category, technology_id, equipment_id):
        self.__production_id = randomStr(16)
        self.__production_category = production_category
        self.__equipment_id = equipment_id
        self.__technology_id = technology_id
        self.__state = "producing"

    def __InitProduction(self):
        '''
        根据equipment_id 得到加载到程序中的设备对象实例
        从数据库中查询具体的工艺 得到具体的工序类 '''

        #查询工艺再得到工序 先放着
        self.working_procedure = WorkingProcedure()

        self.equipment = EquipmentManager.GetInstance().GetEquipmentById(self.__equipment_id)

    def Save(self):
        '''将产品信息写入数据库'''
        pm = ProductionInfo(self.__technology_id, self.__production_id,self.__production_category, self.__equipment_id, self.__state)
        pm.save()

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, value):
        self.__state = value

class ProductionManager:
    '''单列模式'''
    __instance = None

    def __new__(cls, *args, **kwargs):
        return ProductionManager.GetInstance()

    @staticmethod
    def GetInstance():
        if not ProductionManager.__instance:
            '''执行初始化'''
            ProductionManager.__instance = object.__new__(ProductionManager)
            ProductionManager.__instance.__current_productions = [] #留个接口 用append和pop来添加删除 虽然现在同一时间只能生产一个产品
        return ProductionManager.__instance

    def AddProduction(self, production):
        self.__current_productions.append(production)