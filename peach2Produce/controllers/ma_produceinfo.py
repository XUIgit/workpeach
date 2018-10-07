# -*- coding: utf-8 -*-
from app import application
from flask import render_template, request
from models import SearchInfoForm, SearchTechniqueInfoForm
from Business import ProductionManager


@application.route('/ma_produceinfo/searchinfo', methods=['POST', 'GET'])
def ma_produceinfo_searchinfo():
    productions = ProductionManager.SearchProductions(request.form.get('production_id'),request.form.get("production_category"),
                                        request.form.get("status"),request.form.get("result_eval"),request.form.get("process_eval"))
    selected = dict()
    selected['result_eval'] = request.form.get("result_eval")
    selected['process_eval'] = request.form.get("process_eval")
    selected['status'] = request.form.get("status")
    selected['production_id'] = request.form.get("production_id") if request.form.get("production_id") else ""
    selected["technology_id"] = request.form.get("technology_id") if request.form.get("technology_id") else ""
    return render_template('manage/infotableview.html', titleaname='产品信息', selected=selected, productions=productions)

#这里没有重构 工艺方面放到后面来改
@application.route('/ma_techniqueinfo/searchinfo', methods=['POST', 'GET'])
def ma_techniqueinfo_searchinfo():
    searchForm = SearchTechniqueInfoForm.load(request=request)
    return render_template('manage/techniqueManager.html', titleaname='工艺信息', formModel=searchForm)
