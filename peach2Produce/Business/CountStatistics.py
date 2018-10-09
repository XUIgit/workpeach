# -*- coding: utf-8 -*-
'''主要是统计总的运行时间和产品质量'''
from app import db,application
import threading
from models import StatisticalProduceDatas,ProductControlInfo,StatisticalWorkTimeDatas,DeviceInfo,Cost
from datamodels import CollectedDatas
from datetime import datetime,timedelta,date
from sqlalchemy import func,and_
import signalsPool

import time


def Count():
    pass


def StartRecord():
    t=threading.Thread(target=Count)
    t.start()