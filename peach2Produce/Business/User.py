# -*- coding: utf-8 -*-
from models import Users
from app import application
from flask import session, request, abort, redirect, url_for, escape, flash

class User:
    '''管理用户'''

    def __init__(self, username, password):
        self.username = username
        self.password = password

    @staticmethod
    def load(request):
        return User(request.form.get('username'),request.form.get('password'))

    def login(self):
        if Users.login(self.username, self.password):
            return True
        else:
            return False

    @staticmethod
    def logout():
        if not User.isGuest():
            session.pop('username_key')
            session.pop('password')

    @staticmethod
    def isGuest():
        if 'username_key' in session:
            re = Users.query.filter_by(key=session['username_key']).first()
            if re and re.isRight(session['password'], False):
                return False
            else:
                return True
        else:
            return True

    @staticmethod
    def GetUserName():
        if not User.isGuest():
            re = Users.query.filter_by(key=session['username_key']).first()
            return str(escape(re.username))
        else:
            return

    @staticmethod
    def GetUserKey():
        if not User.isGuest():
            re = Users.query.filter_by(key=session['username_key']).first()
            return str(escape(re.key))
        else:
            return

# 注册到模板可以在模板中直接使用
application.add_template_global(User)