# -*- coding: utf-8 -*-
from app import application
from flask import request, url_for, redirect
from models import LocalHostConfig, RemoteHostConfig
from Business import MainManager,EquipmentManager

@application.route('/ma_config/setlocal', methods=['POST'])
def ma_config_setlocal():
    local = LocalHostConfig.load(request)
    local.update()
    return redirect(url_for('ma_index_config'))


@application.route('/ma_config/setremote', methods=['POST'])
def ma_config_setremote():
    remote = RemoteHostConfig.load(request)
    remote.update()
    return redirect(url_for('ma_index_config'))


@application.route('/ma_config/adddevice', methods=['POST'])
def ma_config_adddevice():
    manager = MainManager.GetInstance()
    e = manager.AddEquipment(request.form.get('type'), request.form.get('ip'),
                         int(request.form.get('port')), request.form.get('name'), request.form.get('son_equipment_id'))
    e.run()
    return redirect(url_for('ma_index_config'))

@application.route('/ma_config/removedevice', methods=['POST'])
def ma_config_removedevice():
    id = request.form.get("id")
    e = EquipmentManager.GetInstance().GetEquipmentById(id)
    if e:
        EquipmentManager.GetInstance().DeleteEquipment(e)
    return redirect(url_for('ma_index_config'))



@application.route('/ma_config/connectdevice', methods=['POST'])
def ma_config_connectdevice():
    id = request.form.get('id')
    if id:
        e = EquipmentManager.GetInstance().GetEquipmentById(id)
        if e.status == 'stop':
            e.run()
    return redirect(url_for('ma_index_config'))

