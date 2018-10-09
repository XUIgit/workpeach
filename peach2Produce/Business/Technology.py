
class Technology:
    '''工艺接口'''
    pass

class TechnologyFactory:
    '''工艺工厂类'''

    @staticmethod
    def Create(type):
        if type == TestTechnology:
            return TestTechnology()


class TestTechnology(Technology):

    def __init__(self):
        self.V_THRESHILD_MAX = 100#阈值
        self.V_THRESHILD_MIN = 60
        self.I_THRESHILD_MAX = 30
        self.I_THRESHILD_MIN = 5
        self.AIRCONSUM = 25# 每分钟耗气量(L/min)
        self.WELDINGWIRECONSUM = 0.007# 每分钟焊丝消耗量(kg/min)
