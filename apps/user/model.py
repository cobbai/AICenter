from werkzeug.security import check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer  # 生成具有过期时间的JSON Web 签名（JWS）签名令牌
from apps import login_manager
from apps import db
from flask import current_app  # 应用上下文
from flask_login import UserMixin
from datetime import datetime

from apps.article.model import Article, Blog
from apps.auth.model import Role


# 多对多关系表
class Follow(db.Model):
    __tablename__ = 'follow_relation'
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())


# 用户模型
# UserMixin 提供flask_login运转所需要的方法和属性
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(64), unique=True)  # 用户名
    pwd = db.Column(db.String(128))  # 密码
    email = db.Column(db.String(64), unique=True)  # 邮箱
    # phone = db.Column(db.String(11), unique=True)  # 手机号
    info = db.Column(db.Text())  # 个性简介
    face = db.Column(db.String(255), unique=True)  # 头像
    real_name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    addtime = db.Column(db.DateTime, index=True, default=datetime.utcnow)  # 注册时间
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)  # 最后登录时间
    uuid = db.Column(db.String(255), unique=True)  # 唯一标识符
    confirmed = db.Column(db.Boolean, default=False)  # 未通过邮件确认的用户为False
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))  # "多"的这端

    # "一"的这端：User 调用 Userlog 时用 userlogs, Userlog 调用 User 时用 user
    userlogs = db.relationship('Userlog', backref='user')  # 日志外键关系关联
    articles = db.relationship('Article', backref='user')  #
    blogs = db.relationship('Blog', backref='user', lazy='dynamic')  # 若不加lazy='dynamic'，user调用blogs排序order_by会报错
    comments = db.relationship('Comment', backref='user', lazy='dynamic')  # 评论外键关系关联
    articlecols = db.relationship('Articlecol', backref='user')  # 收藏外键关系关联

    # User 与 Follow 建立多对多关系（关系字段不在表里）
    # foreign_keys：消除外键歧义(因为 Follow中有两个外键)
    # lazy='joined' 使得当调用user.followed.all() 会返回所有关注用户的列表
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan'
                               )
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan'
                                )

    # 返回 User 对象后的字符串表达，方便辨认
    def __repr__(self):
        return '<User %r>' % self.name

    def check_pwd(self, pwd):
        return check_password_hash(self.pwd, pwd)  # 加密并验证用户的密码是否正确

    # 创建User对象的时候，后台检查当前用户的邮箱是否为管理员，否则注册的用户皆为普通用户
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        # 建立了relationship，User调用Role时用 self.role
        if self.role is None:
            if self.email == current_app.config['ADMIN_EMAIL']:
                self.role = Role.query.filter_by(role_name='Administrator').first()
            else:
                self.role = Role.query.filter_by(role_name='User').first()

    # 判断当前user是否有对应权限
    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    # login_manager.user_loader 装饰器把这个函数注册给Flask-Login，在这个扩展需要获取已登录用户的信息时调用。
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # token验证 为self.id生成一个加密签名。expiration过期时间s，
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    # 检验令牌，如果检验通过，就把用户模型中新添加的confirmed 属性设为True。
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    # 重设密码的令牌 token验证
    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    # @staticmethod 使被修饰的方法变为静态方法，可以在不实例化类的情况下直接访问该方法
    # 如果去掉，在方法中加self也可以通过实例化访问方法也是可以集成。
    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.pwd = new_password
        db.session.add(user)
        return True

    # 重设邮箱令牌 token
    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    # 更新用户最后 访问 时间
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    # is_following() is_followed_by() 分别在左右两边的一对多关系中搜索指定用户
    def is_following(self, user):
        if user.id is None:
            return False
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        if user.id is None:
            return False
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    # 把 Follow 实例插入关联表，从而把关注者和被关注者连接起来
    def follow(self, user):
        if not self.is_following(user):
            f = Follow(followed=user)
            self.followed.append(f)
            db.session.commit()

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            self.followed.remove(f)
            db.session.commit()

    # 联结关注用户的所属文章
    # @property 使装饰的方法调用时可以不加()
    @property
    def followed_articles(self):
        return Article.query.join(
            Follow,   # 关联的表
            Follow.followed_id==Article.author_id  # 关联条件
        ).filter(Follow.follower_id == self.id)

    # 联结关注用户的所属Blog
    @property
    def followed_blogs(self):
        return Blog.query.join(
            Follow,  # 关联的表
            Follow.followed_id == Blog.author_id  # 关联条件
        ).filter(Follow.follower_id == self.id)

    # api token验证
    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])


# 用户登录日志
class Userlog(db.Model):
    __tablename__ = 'userlog'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 用户ID
    ip = db.Column(db.String(100))  # 用户IP地址
    addtime = db.Column(db.DateTime, index=True, default=datetime.utcnow)  # 登录时间

    def __repr__(self):
        return '<Userlog %r>' % self.id


