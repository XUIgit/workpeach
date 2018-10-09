from app import application
import datetime
from flask import url_for, request, redirect
from Business import MainManager,ProductionManager


@application.route('/ma_product/manufacture_begin', methods=['POST', 'GET'])
def ma_manufacture_begin():
    if request.method == 'POST':
        production_id = request.form.get('production_id')
        technology_id = request.form.get('technology_id')
        equipment_id = request.form.get('equipment_id')
        production_category = request.form.get('production_category')
    else:
        production_id = request.args.get('production_id')
        technology_id = request.args.get('technology_id')
        equipment_id = request.args.get('equipment_id')
        production_category = request.args.get('production_category')

    begin_time = datetime.datetime.now()

    manager = MainManager.GetInstance()
    manager.AddProduction(production_id, production_category, technology_id, equipment_id, begin_time)

    return redirect(url_for('ma_index_product'))


@application.route('/ma_product/manufacture_end', methods=['POST', 'GET'])
def ma_manufacture_end():
    if request.method == 'POST':
        production_id = request.form.get('production_id')
        process_eval = request.form.get('process_eval')
        result_eval = request.form.get('result_eval')
    else:
        production_id = request.args.get('production_id')
        process_eval = request.args.get('process_eval')
        result_eval = request.args.get('result_eval')

    status = 'FINISHED'
    end_time = datetime.datetime.now()

    production = ProductionManager.GetInstance().GetProductionById(production_id)

    if not production:
        #可以做一些提示，这里直接刷新页面
        return redirect(url_for('ma_index_product'))

    production.end_time = end_time
    production.result_eval = result_eval
    production.process_eval = process_eval
    production.state = status
    production.Save()
    ProductionManager.GetInstance().RemoveProduction(production)


    return redirect(url_for('ma_index_product'))
