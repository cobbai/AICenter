import json
import os
from flask import Blueprint, render_template, request, jsonify
from engines.bert_similarity.bertsimilarity import BertSimilarity
from engines.bert_translation.translation import Translation
from engines.bert_ner.ner import NER
from engines.bert_qa.qa import QA
from engines.bert_classification.classification import Classification
import time

nlp_bp = Blueprint("nlp", __name__, url_prefix='/nlp')

bert_similarity = BertSimilarity(os.getcwd() + "/engines/models/text2vec_base_chinese")
bert_translation_zh_en = Translation(os.getcwd() + "/engines/models/Helsinki-NLP/opus-mt-zh-en")
bert_translation_en_zh = Translation(os.getcwd() + "/engines/models/Helsinki-NLP/opus-mt-en-zh")
bert_ner = NER(os.getcwd() + "/engines/models/bert-base-chinese", os.getcwd() + "/engines/models/ckiplab/bert-base-chinese-ner")
bert_pos = NER(os.getcwd() + "/engines/models/bert-base-chinese", os.getcwd() + "/engines/models/ckiplab/bert-base-chinese-pos")
bert_qa = QA(os.getcwd() + "/engines/models/uer/roberta-base-chinese-extractive-qa")
bert_classification = Classification(os.getcwd() + "/engines/models/total_category1_score_new_0.5")


@nlp_bp.route('/SentenceSimilarity/', methods=['GET', 'POST'])
def SentenceSimilarity():

    if request.method == "POST":
        data = {}
        for item in request.form.lists():
            data[item[0]] = item[1]
        t1 = time.time()
        result = bert_similarity.compute(data)
        result["time_cost"] = round(time.time() - t1, 2)
        return json.dumps(result)

    return render_template("nlp/SentenceSimilarity.html")


@nlp_bp.route('/NER/', methods=['GET', 'POST'])
def NER():
    if request.method == "POST":
        content = list(request.form.lists())
        result = {}
        t1 = time.time()
        if content[0][1][0] == '#text1':
            result["ans"] = bert_ner.compute(content[0][1][1])
        if content[0][1][0] == '#text2':
            result["ans"] = bert_pos.compute_pos(content[0][1][1])
        result["time_cost"] = round(time.time() - t1, 2)
        return json.dumps(result)

    return render_template("nlp/NER.html")


@nlp_bp.route('/Translation/', methods=['GET', 'POST'])
def Translation():
    if request.method == "POST":
        content = list(request.form.lists())
        result = {}
        t1 = time.time()
        if content[0][1][0] == '#text1':
            result = bert_translation_zh_en.translation(content[0][1][1])[0]
        if content[0][1][0] == '#text2':
            result = bert_translation_en_zh.translation(content[0][1][1])[0]
        result["time_cost"] = round(time.time() - t1, 2)
        return json.dumps(result)

    return render_template("nlp/Translation.html")


@nlp_bp.route('/QuestionAnswering/', methods=['GET', 'POST'])
def QuestionAnswering():
    if request.method == "POST":
        content = request.form.to_dict()
        result = {}
        t1 = time.time()
        result["ans"] = bert_qa.compute(content["context"], content["question"])["answer"]
        result["time_cost"] = round(time.time() - t1, 2)
        return json.dumps(result)

    return render_template("nlp/QA.html")


@nlp_bp.route('/TextClassification/', methods=['GET', 'POST'])
def TextClassification():
    if request.method == "POST":
        content = request.form.to_dict()
        result = {}
        t1 = time.time()
        result["ans"] = bert_classification.compute(content["context"])
        result["time_cost"] = round(time.time() - t1, 2)
        return json.dumps(result)

    return render_template("nlp/TextClassification.html")