from apps import create_app, db
from flask import render_template, request, jsonify
# pip3 install flask_script
from flask_script import Manager
# pip3 install flask_migrate
# python app.py db_command init  -->  migrations文件夹
# python app.py db_command migrate -m "": 每次更新 model 后要migrate，自动创建迁移脚本
# 若migrate报错，则说明versions下的版本号没有对应上，要删除多余版本号
# python app.py db_command upgraade : 最后会执行versions版本里upgrade里的语句
from flask_migrate import Migrate, MigrateCommand
from datetime import datetime

from apps.auth.model import Tag

app = create_app()
app.logger.info("app初始化完毕")

# 404
@app.errorhandler(404)
def page_not_found(e):
    # 当客户端接受的response中包含JSON且不包含HTML时，生成JSON响应
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found', 'message': e})
        response.status_code = 404
        return response
    return render_template("404.html"), 404


# 403
@app.errorhandler(403)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'forbidden', 'message': e})
        response.status_code = 403
        return response
    return render_template("403.html"), 403


# 500
@app.errorhandler(500)
def internal_server_error(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'Internal Server Error', 'message': e})
        response.status_code = 500
        return response
    return render_template('500.html'), 500


# 上下应用处理器(封装全局变量,展现到模板里,将我们的定义变量在所有模板中可见,
# 返回结果必须是 dict, 然后其 key 将会作为变量在所有模板中可见)
@app.context_processor
def tpl_extra():
    article_tags = Tag.query.filter_by(source="文章标签").all()
    nlp_tags = Tag.query.filter_by(source="NLP模型标签").all()
    data = dict(
        current_time=datetime.utcnow(),  # base.html 中的 moment(current_time)
        article_tags=article_tags,
        nlp_tags=nlp_tags,
    )
    return data


manage = Manager(app)


# 自定义添加命令
@manage.command
def define_arg():
    print("自定义参数测试")


# 命令工具
# python app.py db_command migrate -m "更新内容"
# python app.py db_command upgrade
migrate = Migrate(app, db)  # 连接app
manage.add_command("db_command", MigrateCommand)  # 连接manage

# 推送应用上下文
# 解决上下文问题：app.py必须要导入模型model，否则无法migrate
# app.app_context().push()


if __name__ == '__main__':
    # 函数 run() 启动本地服务器来运行我们的应用app
    # app.run(host='0.0.0.0')  # 这让你的操作系统去监听所有公开的 IP。外网访问时需要输入 本服务器IP + 关闭防火墙
    # app.run(port=5000)
    manage.run()  # python app.py runserver
