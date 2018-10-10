# -*- coding: utf-8 -*-


#flask应用程序实例模块
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


application = Flask(__name__) #主程序实例
application.config.from_object('config')#应用配置
db = SQLAlchemy(application)#使用mysql数据库

