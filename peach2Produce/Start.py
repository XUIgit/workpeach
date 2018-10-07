# -*- coding: utf-8 -*-
#从这个文件开始执行
from app import application

from Controllers import * #导入所有控制器
from Business import MainManager,StartAgv

if __name__ == '__main__':
    manager = MainManager.GetInstance()
    manager.RunAllEquipment()#运行所有的设备
    StartAgv()#开启获取agv小车的数据的线程
    application.run(host=application.config['HOST'], port=application.config['PORT'], use_reloader=False)