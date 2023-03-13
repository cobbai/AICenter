import json
import os
from flask import Blueprint, render_template, request, jsonify, current_app, abort
from flask_login import login_required, current_user
from functools import wraps
from werkzeug.utils import secure_filename
from engines.bert_similarity.bertsimilarity import BertSimilarity
from engines.bert_translation.translation import TextTranslation
from engines.bert_ner.ner import NamedEntityRecognition
from engines.bert_qa.qa import QA
from engines.bert_classification.classification import Classification
from engines.bert_textgeneration.textgeneration import TextGenerate
import time
from queue import Queue
import threading

nlp_bp = Blueprint("nlp", __name__, url_prefix='/nlp')
q = Queue()

def need_permission(perm):
    # 自定义装饰器：角色权限访问控制装饰器
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.can(perm):
                abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def train_func(app, content, file_path, q):
    with app.app_context():
        bert_classification = Classification(os.getcwd() + "/engines/models/", file_path)
        bert_classification.train(content["feature"], content["label"], float(content["frac"]), int(content["epoch"]), q)


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
    content = request.form.to_dict()
    # 预测
    if request.method == "POST" and content.get("context") is not None:
        result = {}
        t1 = time.time()
        bert_classification = Classification(os.getcwd() + "/engines/models/")
        result["ans"] = bert_classification.compute(content["context"])
        del bert_classification
        result["time_cost"] = round(time.time() - t1, 2)
        return json.dumps(result)

    return render_template("nlp/TextClassification.html", dataview="")


@nlp_bp.route('/TextClassificationTrainer/', methods=['GET', 'POST'])
@login_required
@need_permission(Permission.MODEL)
def TextClassificationTrainer():
    content = request.form.to_dict()
    file_path = os.getcwd() + "/engines/datasets/job_detail_file.txt"
    # 上传数据
    if request.method == "POST" and content.get("sep") is not None:
        files = request.files.get("customerfile")
        if request.form.get("sep") == "1":
            sep = ","
        else:
            sep = "\t"

        if files.filename != '':
            file_path = os.path.join(current_app.config['UPLOAD_DIR'], secure_filename(files.filename))
            files.save(file_path)

        dataview = []
        with open(file_path, "r", encoding="utf-8-sig") as r:
            header = r.readline().strip("\n").split(sep)
            dataview.append(header)
            for i in range(5):
                line = r.readline().strip("\n").split(sep)[:len(header)]
                dataview.append(line)
        return render_template("nlp/TextClassificationTrainer.html", dataview=dataview)
    # 训练
    if request.method == "POST" and len(content) > 1:
        result = {}
        t1 = time.time()
        # 新线程后台训练
        app = current_app._get_current_object()
        thr = threading.Thread(name="train_thread", target=train_func, args=[app, content, file_path, q])
        # thr.daemon = 1
        thr.start()
        result["time_cost"] = round(time.time() - t1, 2)
        return jsonify(result)
    return render_template("nlp/TextClassificationTrainer.html", dataview="")


@nlp_bp.route('/getlog/', methods=['GET', 'POST'])
def getlog():
    # print(threading.activeCount())
    # print(threading.enumerate())
    if q.empty():
        return jsonify({"data": "empty"})
    else:
        a = q.get()  # get不到会阻塞
        return jsonify({"data": a})


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