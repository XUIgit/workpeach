from Business.Equipments import EquipmentManager,EquipmentFactory
from Business.Production import ProductionManager,Production


class MainManager:
    '''主管理器, 单列模式'''
    __instance = None

    def __new__(cls, *args, **kwargs):
        return MainManager.GetInstance()

    @staticmethod
    def GetInstance():
        if not MainManager.__instance:
            '''执行初始化'''
            MainManager.__instance = object.__new__(MainManager)
            EquipmentManager.GetInstance()#第一次调用获取实例 在其中进行初始化
            ProductionManager.GetInstance()
            MainManager.__instance.__RunAllEquipment()
        return MainManager.__instance

    def __RunAllEquipment(self):
        for equipment in EquipmentManager.GetInstance().GetAllEquipments():
            equipment.run()

    def AddProduction(self, production_category, technology_id, equipment_id):
        return ProductionManager.GetInstance().AddProduction(production_category, technology_id, equipment_id)

    def AddEquipment(self, type, ip, port, name, son_equipment_id=None):
        return EquipmentManager.GetInstance().AddEquipment(type, ip, port, name, son_equipment_id)

    def RemoveProduction(self, production):
        ProductionManager.GetInstance().RemoveProduction(production)

    def DeleteEquipment(self, equipment):
        EquipmentManager.GetInstance().DeleteEquipment(equipment)