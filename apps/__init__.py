from flask import Flask
# pip3 install flask-wtf
# pip install email_validator -i https://pypi.douban.com/simple/
from flask_wtf import CSRFProtect
import settings
from extends import *
import logging

from apps.article.views import article_bp
from apps.user.views import user_bp
from apps.auth.views import auth_bp
from apps.nlp.views import nlp_bp
from apps.cv.views import cv_bp

"""
__init__.py 有两个作用：
一是包含应用工厂；
二是 告诉 Python flaskr 文件夹应当视作为一个包。
"""

def create_app():
    # 初始化falsk框架
    # WSGI server：Web服务器网关接口，是为Python语言定义的 “Web服务器” 和 “Web应用程序或框架” 之间的一种简单而通用的 “接口”
    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    # csrf 需要 setting.py 配置 SECRET_KEY（session也要）
    # csrf = CSRFProtect(app)

    # 加载配置信息
    app.config.from_object(settings.DevelopmentConfig)

    # initialize logging class
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 关联ORM
    db.init_app(app)

    # 初始化bootstrap
    bootstrap.init_app(app)

    # 浏览器转化时间
    moment.init_app(app)

    # 登陆验证
    login_manager.session_protection = "strong"
    login_manager.login_view = "user.user_login"
    login_manager.login_message = "必须登陆后才能访问"
    login_manager.login_message_category = "warning"
    login_manager.init_app(app)

    # 邮箱
    mail.init_app(app)

    # Markdown
    pagedown.init_app(app)

    # 初始化restful
    # api.init_app(app)

    # 跨域问题
    # cors.init_app(app=app, supports_credentials=True)

    # 初始化缓存Cache
    redis_config = {
        'CACHE_TYPE': 'redis',  # 缓存类型用redis
        'CACHE_REDIS_HOST': 'free.idcfengye.com',  # '192.168.31.54',  # redis 主机地址
        'CACHE_REDIS_PORT': 10173,  # redis 端口号默认6379
        # 'CACHE_REDIS_PASSWORD': 'root',
    }
    cache.init_app(app, config=redis_config)  # flask缓存到redis数据库

    # 注册蓝图

    app.register_blueprint(article_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(nlp_bp)
    app.register_blueprint(cv_bp)

    # 调试用
    from apps.temp.views import temp_bp
    app.register_blueprint(temp_bp)
    # print(app.url_map)
    return app



