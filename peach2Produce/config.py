# -*- coding: utf-8 -*-
from app import application

application.debug = True

application.secret_key = '0pMfZOHyqVwRSYrtmgI89Pc1hs4ezknA'

PORT = 80
HOST = '0.0.0.0'

AGVHOST = '0.0.0.0'
AGVPORT = 9001

sqlusername = 'xui'
sqlpassword = '123456'
sqlport = '3306'
sqldatabasename = 'peach'

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@localhost:{}/{}?charset=utf8'.format(sqlusername, sqlpassword, sqlport,
                                                                                      sqldatabasename)
SQLALCHEMY_TRACK_MODIFICATIONS = True

# 需要进行身份认证的控制器 认证失败则重定向到无权限页面
NEED_AUTH = ['ma_index', 'ma_config', 'ma_workshop', 'ma_produceinfo', 'ma_producreport']

REMOTEURL = ''
LOCALID = ''
INTERVAL = 0

# 存在的设备 ID:info
DEVICES = {}


# 一些临时的工艺参数
# 电压阈值 通过起来判断机器人是否记时
VTHRESHILD = 500
# 每分钟耗气量(L/min)
AIRCONSUM = 25
# 每分钟焊丝消耗量(kg/min)
WELDINGWIRECONSUM = 0.007
