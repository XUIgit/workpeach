class Equipment:
    '''设备的基类'''

    def __init__(self, id, unique_id, type, name, sql_model, desc):
        self.__id = id
        self.__unique_id = unique_id
        self.__type = type
        self.__name = name
        self.__sql_model = sql_model
        self.__desc = desc

    def run(self):
        pass


class WeldingEquipment(Equipment):
    '''焊接设备的基类'''

    def __init__(self, id, unique_id, type, name, sql_model, desc):
        Equipment.__init__(self, id, unique_id, type, name, sql_model, desc)
        pass

    def run(self):
        pass


class Robot(Equipment):

    '''焊接设备的基类'''

    def __init__(self, id, unique_id, type, name, sql_model, desc):
        Equipment.__init__(self, id, unique_id, type, name, sql_model, desc)
        pass

    def run(self):
        pass


class Collector(Equipment):
    '''采集器'''

    def __init__(self, id, unique_id, type, name, sql_model, desc):
        Equipment.__init__(self, id, unique_id, type, name, sql_model, desc)
        pass

    def run(self):
        pass


class WeldingGun(WeldingEquipment):
    '''焊枪'''

    def __init__(self, id, unique_id, type, name, sql_model, desc):
        WeldingEquipment.__init__(self, id, unique_id, type, name, sql_model, desc)
        pass

    def run(self):
        pass


class CuttingMachine(WeldingEquipment):
    '''切割机'''

    def __init__(self, id, unique_id, type, name, sql_model, desc):
        WeldingEquipment.__init__(self, id, unique_id, type, name, sql_model, desc)
        pass

    def run(self):
        pass


class EquipmentManager:
    pass