import signalsPool
from app import db, application
from models import RobotRunInfo, ProductControlInfo, TechniqueInfo, DeviceInfo
import threading


def signals_robot_start_callback(sender, *args, **kwargs):
    pass


def signals_robot_stop_callback(sender, *args, **kwargs):
    pass


def signals_product_begin_callback(product_id, *args, **kwargs):
    pass


def signals_product_finish_callback(product_id, *args, **kwargs):
    pass

# 机器人
signalsPool.ROBOT_START.connect(signals_robot_start_callback)
signalsPool.ROBOT_STOP.connect(signals_robot_stop_callback)

# 产品生产
signalsPool.PRODUCT_BEGIN.connect(signals_product_begin_callback)
signalsPool.PRODUCT_FINISHED.connect(signals_product_finish_callback)
