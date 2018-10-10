# -*- coding: utf-8 -*-
'''这里放所有的业务逻辑的模块'''
from Business.MainManager import MainManager
from Business.User import User
from Business.Equipments import EquipmentManager
from Business.Production import ProductionManager
from Business.Agv import StartAgv
from Business.CountStatistics import StartCount
from Business.Record import StartRecord

from app import application,db

application.add_template_global(MainManager.GetInstance(), 'main_manager')
application.add_template_global(EquipmentManager.GetInstance(), 'equipment_manager')
application.add_template_global(ProductionManager.GetInstance(), 'production_manager')


from models import LocalHostConfig,RemoteHostConfig,Users
#这些数据库中没有需要先设置一个初始值
if not LocalHostConfig.query.first():
    l = LocalHostConfig('123456789', 1000)
    l.save()

if not RemoteHostConfig.query.first():
    r = RemoteHostConfig("http://uma.net.cn:8000")
    r.save()

# 添加用户
if not Users.query.first():
    u = Users('admin', '123456', '123456@qq.com')
    db.session.add(u)
    db.session.commit()