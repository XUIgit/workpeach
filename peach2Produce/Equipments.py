from app import db
from models import EquipmentInfo
from datamodels import CollectedDatas
import socket
import time
import signalsPool
import threading

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
        self.status = 'stop'

    def save(self):
        if self.__exist_in_db:#存在于数据库中直接提交更新
            db.session.commit()
        else:#不存在则先添加
            db.session.add(self.__sql_model)
            db.session.commit()
            self.__exist_in_db = True

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

    def GetCollector(self):#返回该设备连接的采集器
        if not self.__collector:
            if not self.son_equipment_id:#不存在collector
                return None
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
        if self.status == 'stop':
            self.thread = threading.Thread(target=Collector.__socket_run,args=(self,))
            self.thread.start()

    def __socket_run(self):
        '''执行tcp通信和数据储存的线程函数'''
        sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.status = "connecting"
            sc.connect((self.ip, self.port))
        except Exception as e:
            print(e)

        for try_times in range(1, 3):
            try:
                self.status = "reconnecting"
                sc.connect((self.ip, self.port))
            except Exception as err:
                print('err:' + str(err))
                print(self.name+' 连接异常 尝试重新连接{}次'.format(try_times))
                time.sleep(1)

        last_v = 0
        last_e = 0
        collected_num_thershold = 0
        while True:
            try:
                data = sc.recv(8)
                e = (data[2] * 256 + data[3]) / 100  # 文档中电压与电流 与实际相反
                v = (data[0] * 256 + data[1]) / 100
                t = (data[4] * 256 + data[5]) / 100

                if (v != 0 or e != 0) and (last_v == 0 and last_e == 0):
                    signalsPool.ROBOT_START.send(id, time=time.time())
                if (v == 0 or e == 0) and (last_v != 0 and last_e != 0):
                    signalsPool.ROBOT_STOP.send(id, time=time.time())
                last_v = v
                last_e = e
                collected_num_thershold += 1
                if collected_num_thershold >= 100:
                    #建立好产品模型后在来处理
                    #one = CollectedDatas(unique_id, productId, e, v, t, produce_status, robotId)
                    #one.save()
                    collected_num_thershold = 0
            except socket.error as e:
                print(e)
                self.status = "stop"
                return
            except Exception as err:
                print('err:' + str(err))
                self.status = "stop"
                return


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
        equipments = EquipmentInfo.query.filter_by(type=type)
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
            sql_model = EquipmentInfo(type=type)
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
            EquipmentManager.__instance.__allequipments = EquipmentManager.__instance.__collectors + EquipmentManager.__instance.__robots + EquipmentManager.__instance.__cuttingmachines + EquipmentManager.__instance.__weldingguns
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
        else:
            raise ValueError("type error")
        self.__allequipments.append(e)
        return e
    #删除设备
    def DeleteEquipment(self, unique_id):
        equipment = self.GetEquipmentById(unique_id)
        #从相应的设备列表中删除
        if type(equipment) == Collector:
            self.__collectors.remove(equipment)
        elif type(equipment) == Robot:
            self.__robots.remove(equipment)
        elif type(equipment) == CuttingMachine:
            self.__cuttingmachines.remove(equipment)
        elif type(equipment) == WeldingGun:
            self.__weldingguns.remove(equipment)
        else:
            raise ValueError("equipment must be a instance of Euipment")
        self.__allequipments.remove(equipment)
        #从数据库中删除
        db.session.delete(equipment)
        db.session.commit()

    def GetEquipmentById(self, unique_id):
        '''根据设备id返回已经加载到了程序中的设备对象'''
        for equipment in self.GetAllEquipments():
            if equipment.unique_id == unique_id:
                return equipment
        print("没有找到 "+unique_id+" 的设备")
        return None

    def GetAllEquipments(self):
        return self.__allequipments

    def GetAllCollectors(self):
        return self.__collectors

    def GetAllRobots(self):
        return self.__robots

    def GetAllWeldingGun(self):
        return self.__cuttingmachines

    def GetAllCuttingMachine(self):
        return self.__weldingguns