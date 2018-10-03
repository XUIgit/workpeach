# -*- coding: utf-8 -*-
from Business import User
from app import application
from flask import session, request, abort, redirect, url_for, escape, flash

# 使用session 默认记住(即过期时间长)

# 实际登录动作
@application.route('/user/login', methods=['POST', 'GET'])
def user_login():
    if request.method == 'POST':
        if not User.isGuest():
            return redirect(url_for('index_index'))
        else:
            user = User.load(request)
            if user.login():
                return redirect(url_for('ma_index_index'))
            else:
                flash(u'你输入的账户或者密码有错误', 'user_login_error')
                return redirect(url_for('index_login'))
    else:
        abort(404)


# 新建用户动作
'''
@application.route('/user/signup', methods=['POST', 'GET'])
def user_signup():
    if request.method == 'POST':
        if not User.isGuest():
            return redirect(url_for('index_index'))
        else:
            user = User(username=request.form['username'],
                        password=request.form['password'],
                        email=request.form['email'],
                        )
            if user.save():
                return redirect(url_for('index_index'))
            else:
                flash(u'注册失败', 'user_add_error')
                return redirect(url_for('index_login'))
    else:
        abort(404)'''


# 注销动作
@application.route('/user/logout', methods=['POST', 'GET'])
def user_logout():
    User.logout()
    return redirect(url_for('index_index'))