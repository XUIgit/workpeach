# -*- coding: utf-8 -*-
#从这个文件开始执行
from app import application
from app import db

from Controllers import * #导入所有控制器
from Business import MainManager

# 创建所有需要的表(存在则不会创建)
db.create_all()

if __name__ == '__main__':
    manager = MainManager.GetInstance()
    application.run(host=application.config['HOST'], port=application.config['PORT'], use_reloader=False)