import json
import os
from flask import Blueprint, render_template, request, jsonify
from engines.bert_similarity.bertsimilarity import BertSimilarity
import time

nlp_bp = Blueprint("nlp", __name__, url_prefix='/nlp')


sim_model = BertSimilarity(os.getcwd() + "/engines/bert_similarity/text2vec_base_chinese")


@nlp_bp.route('/SentenceSimilarity/', methods=['GET', 'POST'])
def SentenceSimilarity():

    if request.method == "POST":
        data = {}
        for item in request.form.lists():
            data[item[0]] = item[1]
        t1 = time.time()
        result = sim_model.compute(data)
        result["time_cost"] = round(time.time() - t1, 2)
        return json.dumps(result)

    return render_template("nlp/SentenceSimilarity.html")


@nlp_bp.route('/TextClassification/', methods=['GET', 'POST'])
def TextClassification():
    return "ok"


@nlp_bp.route('/Translation/', methods=['GET', 'POST'])
def Translation():
    return "ok"

