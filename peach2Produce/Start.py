# -*- coding: utf-8 -*-
#从这个文件开始执行
from app import application,db

# 创建所有需要的表(存在则不会创建)
import models
db.create_all()

from Controllers import * #导入所有控制器
from Business import MainManager,StartAgv,StartCount,StartRecord

if __name__ == '__main__':
    manager = MainManager.GetInstance()
    manager.RunAllEquipment()#运行所有的设备
    StartAgv()#开启获取agv小车的数据的线程
    StartCount()#开启线程开始统计
    StartRecord()#开启线程记录设备各种状态的运行时间
    application.run(host=application.config['HOST'], port=application.config['PORT'], use_reloader=False)