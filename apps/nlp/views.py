import json
import os
from flask import Blueprint, render_template, request, jsonify
from engines.bert_similarity.bertsimilarity import BertSimilarity
from engines.bert_translation.translation import TextTranslation
from engines.bert_ner.ner import NamedEntityRecognition
from engines.bert_qa.qa import QA
from engines.bert_classification.classification import Classification
from engines.bert_textgeneration.textgeneration import TextGenerate
import time
nlp_bp = Blueprint("nlp", __name__, url_prefix='/nlp')


@nlp_bp.route('/SentenceSimilarity/', methods=['GET', 'POST'])
def SentenceSimilarity():
    if request.method == "POST":
        data = {}
        for item in request.form.lists():
            data[item[0]] = item[1]
        t1 = time.time()
        bert_similarity = BertSimilarity(os.getcwd() + "/engines/models/text2vec_base_chinese")
        result = bert_similarity.compute(data)
        result["time_cost"] = round(time.time() - t1, 2)
        del bert_similarity
        return json.dumps(result)

    return render_template("nlp/SentenceSimilarity.html")


@nlp_bp.route('/NER/', methods=['GET', 'POST'])
def NER():
    if request.method == "POST":
        content = list(request.form.lists())
        result = {}
        t1 = time.time()
        if content[0][1][0] == '#text1':
            bert_ner = NamedEntityRecognition(os.getcwd() + "/engines/models/bert-base-chinese",
                           os.getcwd() + "/engines/models/ckiplab/bert-base-chinese-ner")
            result["ans"] = bert_ner.compute(content[0][1][1])
            del bert_ner
        if content[0][1][0] == '#text2':
            bert_pos = NamedEntityRecognition(os.getcwd() + "/engines/models/bert-base-chinese",
                           os.getcwd() + "/engines/models/ckiplab/bert-base-chinese-pos")
            result["ans"] = bert_pos.compute_pos(content[0][1][1])
            del bert_pos
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
            bert_translation_zh_en = TextTranslation(os.getcwd() + "/engines/models/Helsinki-NLP/opus-mt-zh-en")
            result = bert_translation_zh_en.translation(content[0][1][1])[0]
            del bert_translation_zh_en
        if content[0][1][0] == '#text2':
            bert_translation_en_zh = TextTranslation(os.getcwd() + "/engines/models/Helsinki-NLP/opus-mt-en-zh")
            result = bert_translation_en_zh.translation(content[0][1][1])[0]
            del bert_translation_en_zh
        result["time_cost"] = round(time.time() - t1, 2)
        return json.dumps(result)

    return render_template("nlp/Translation.html")


@nlp_bp.route('/QuestionAnswering/', methods=['GET', 'POST'])
def QuestionAnswering():
    if request.method == "POST":
        content = request.form.to_dict()
        result = {}
        t1 = time.time()
        bert_qa = QA(os.getcwd() + "/engines/models/uer/roberta-base-chinese-extractive-qa")
        result["ans"] = bert_qa.compute(content["context"], content["question"])["answer"]
        del bert_qa
        result["time_cost"] = round(time.time() - t1, 2)
        return json.dumps(result)

    return render_template("nlp/QA.html")


@nlp_bp.route('/TextClassification/', methods=['GET', 'POST'])
def TextClassification():
    if request.method == "POST":
        content = request.form.to_dict()
        result = {}
        t1 = time.time()
        bert_classification = Classification(os.getcwd() + "/engines/models/total_category1_score_new_0.5")
        result["ans"] = bert_classification.compute(content["context"])
        del bert_classification
        result["time_cost"] = round(time.time() - t1, 2)
        return json.dumps(result)

    return render_template("nlp/TextClassification.html")


@nlp_bp.route('/getlog/', methods=['GET', 'POST'])
def getlog():

    return ""

@nlp_bp.route('/TextGeneration/', methods=['GET', 'POST'])
def TextGeneration():
    if request.method == "POST":
        content = request.form.to_dict()
        result = {}
        t1 = time.time()
        bert_textgeneration = TextGenerate(os.getcwd() + "/engines/models/uer/gpt2-chinese-cluecorpussmall")
        result["ans"] = bert_textgeneration.compute(content["context"])[0]["generated_text"]
        del bert_textgeneration
        result["time_cost"] = round(time.time() - t1, 2)
        return json.dumps(result)

    return render_template("nlp/TextGeneration.html")