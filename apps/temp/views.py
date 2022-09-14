from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, g, make_response, flash, abort
from apps import cache
from apps.article.form import ArticlePostForm
from apps.temp.form import testForm
from apps.temp.model import *  # 不论用不用Model，都要在views中导入model，否则无法migrate

temp_bp = Blueprint("temp", __name__, url_prefix='/temp')


# bootstrap study
@temp_bp.route("/chart")
def chart():
    return render_template("temp/chart_temp.html")

# bootstrap study
@temp_bp.route("/temp0")
def temp_0():
    return render_template("temp/bootstrap.html")


# 动态路由
@temp_bp.route("/<name>?page=<page>&version=<version>")
def temp_1(name, page, version):
    return "Helllo, {}, {}, {}".format(name, page, version)


# 重定向
@temp_bp.route("/urlfor/")
def temp_2():
    return redirect(url_for("temp.temp_1", name="cobb", page=2, version=1))


# 世界时间
@temp_bp.route("/")
def temp_index():
    return render_template("base.html", current_time=datetime.utcnow())


# redis
@temp_bp.route("/redis")
# @cache.cached(timeout=50)  # 页面缓存
def temp_redis():
    key = "testKey"
    val = "哈哈哈哈" + str(1)
    cache.set(key, val, timeout=180)
    return cache.get(key)

# 快速创建表单
@temp_bp.route("/quickform/", methods=['GET', 'POST'])
def quickForm():
    form = testForm()
    if form.validate_on_submit():
        data = form.data

        # session 请求上下文
        session["name"] = data["name"]
        session["email"] = data["email"]
        session["phone"] = data["phone"]
        print("session 请求上下文：", session)

        # 存入数据库
        tempuser = TempUser(
            username=data['name'],
            email=data['email'],
            phone=data['phone'],
        )
        db.session.add(tempuser)
        db.session.commit()
        flash('恭喜您,注册成功!', 'info')  # 前端要用 get_flashed_messages() 获取消息，类似消息队列
        # return redirect(url_for('temp.temp_1', name=data["name"], page=data["phone"], version=data["email"]))
        return redirect(url_for('temp.quickForm'))
    return render_template("temp/quick_form.html", form=form)

