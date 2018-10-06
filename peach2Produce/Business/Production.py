# -*- coding: utf-8 -*-
from utils import randomStr
from models import ProductionInfo
from Business.Equipments import EquipmentManager

'''
基本原则，尽量调用Manager里的操作函数，而不是相应对象本身的
'''

class WorkingProcedure:
    '''工序类  工序类中包含具体工艺流程'''
    pass

class Production:
    '''生产模型 包含具体的产品信息'''
    def __init__(self, production_id, production_category, technology_id, equipment_id,begin_time):
        self.__production_id = production_id
        self.__production_category = production_category
        self.__equipment_id = equipment_id
        self.__technology_id = technology_id
        self.__state = "PRODUCING"
        self.__process_eval = "UNCHECK"
        self.__result_eval = "UNCHECK"
        self.__begin_time = begin_time
        self.__end_time = 100000

    def CheckTechnology(self):
        '''
        根据equipment_id 得到加载到程序中的设备对象实例
        从数据库中查询具体的工艺 得到具体的工序类 '''

        #查询工艺再得到工序 先放着
        self.working_procedure = WorkingProcedure()

        self.equipment = EquipmentManager.GetInstance().GetEquipmentById(self.__equipment_id)

    def Save(self):
        p = ProductionInfo.query.filter_by(production_id=self.production_id).first()
        if p:
            p.technology_id = self.__technology_id
            p.production_id = self.production_id
            p.production_category = self.__production_category
            p.equipment_id = self.equipment_id
            p.production_state = self.state
            p.result_eval = self.result_eval
            p.process_eval = self.process_eval
            p.begin_time = self.__begin_time
            p.end_time = self.end_time
            p.update()
        else:
            e = ProductionInfo(self.__technology_id, self.__production_id, self.__production_category,
                               self.__equipment_id, self.__state, self.process_eval, self.result_eval,self.__begin_time,self.end_time)
            e.save()

    @property
    def end_time(self):
        return self.__end_time

    @end_time.setter
    def end_time(self, value):
        self.__end_time = value

    @property
    def result_eval(self):
        return self.__result_eval

    @result_eval.setter
    def result_eval(self, value):
        self.__result_eval = value

    @property
    def process_eval(self):
        return self.__process_eval

    @process_eval.setter
    def process_eval(self, value):
        self.__process_eval = value

    @property
    def production_id(self):
        return self.__production_id

    @property
    def equipment_id(self):
        return self.__equipment_id

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

    def AddProduction(self, production_id, production_category, technology_id, equipment_id, begin_time):
        production = Production(production_id, production_category, technology_id, equipment_id,begin_time)
        production.CheckTechnology()#查询工艺 并赋值到自身
        production.Save()
        self.__current_productions.append(production)
        return production

    def GetProductionById(self, production_id):
        for production in self.__current_productions:
            if production.production_id == production_id:
                return production

    def RemoveProduction(self, production):
        '''从程序中移除程序'''
        self.__current_productions.remove(production)