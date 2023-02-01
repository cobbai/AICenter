import os
class Config:
    # flask_wtf
    # 设置 session 密钥
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cobb')

    # RecaptchaField wtform验证码需要设置的公钥、私钥、参数
    # RECAPTCHA_PUBLIC_KEY = 'sdasdasdad'
    # RECAPTCHA_PRIVATE_KEY = 'sdasdasdasdasdad'
    # RECAPTCHA_PARAMETERS = {'hl': 'zh', 'render': 'explicit'}
    # RECAPTCHA_DATA_ATTRS = {'theme': 'dark'}

    # 项目路径
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # __file__: settings.py的位置
    # 静态文件夹路径
    STATIC_DIR = os.path.join(BASE_DIR, "static")
    TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
    UPLOAD_DIR = os.path.join(STATIC_DIR, "upload")


class DevelopmentConfig(Config):
    ENV = "development"
    DEBUG = True

    # SQLAlchemy
    # 连接数据库：SQLALCHEMY会从配置环境文件中找到这两个变量，将其值作为数据库连接
    # 数据库+驱动://用户名：密码@主机地址:端口/数据库
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@127.0.0.1:3306/aicenter"
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 降低内存消耗

    # Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.qq.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = True
    MAIL_USERNAME = "413075854@qq.com"
    MAIL_PASSWORD = "vdmjebjyewulbhed"

    ADMIN_EMAIL = "xjhmbb@sina.com"


class ProductionConfig(Config):
    ENV = "production"
    DEBUG = False

    # Email
    MAIL_SERVER = 'smtp.sina.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
