# pip3 install pymysql
# pip3 install flask-sqlalchemy
from flask_sqlalchemy import SQLAlchemy
# pip3 install flask-bootstrap
from flask_bootstrap import Bootstrap
# pip3 install flask-moment
from flask_moment import Moment
# pip3 install flask-login
from flask_login import LoginManager
# pip3 install flask-mail
from flask_mail import Mail
# pip3 install flask-pagedown
# pip3 install bleach
# pip3 install markdown
from flask_pagedown import PageDown

# pip3 install flask-caching
# pip3 install redis
from flask_caching import Cache
# pip3 install flask-restful
# from flask_restful import Api
# pip3 install flask-cors
# from flask_cors import CORS

# 创建ORM
db = SQLAlchemy()

# 初始化Bootstrap，在模板 base.html {% extends "bootstrap/base.html" %}
# Flask-Bootstrap 的基模板提供了一个网页骨架，引入了Bootstrap 的所有CSS 和JavaScript文件。
# 匹配wtform {% import "bootstrap/wtf.html" as wtf %}
bootstrap = Bootstrap()

# 在浏览器中渲染日期和时间。
# jinjia2模板中添加 scripts: {{ moment.include_moment() }}
moment = Moment()

# 登录验证
# 在model中的User需要继承UserMixin，并用@login_manager.user_loader注册获取用户信息的函数,验证用户身份
# 在view中用@login_required只让通过身份验证的用户访问
# login路由用login_user()保存用户会话
# logout路由用logout_user()删除用户会话
# 上下文变量current_user可以获取User表的字段
login_manager = LoginManager()

# 邮箱
mail = Mail()

# Markdown
# jinjia2模板中添加 scripts: {{ pagedown.include_pagedown() }}
pagedown = PageDown()

# 缓存数据库redis
cache = Cache()

# 前后端分离 restful
# api = Api()

# 跨域问题 cors
# cors = CORS()
