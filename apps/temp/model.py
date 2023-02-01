from apps import db


# 定义表模型
class TempRole(db.Model):
    # 在数据库中使用的表名
    __tablename__ = 'temp_roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('TempUser', backref='temprole')  # 定义关系型数据库的 关系。User通过role获取Role对象，Role通过users获取User对象

    # __repr()__ 方法，返回一个具有可读性的字符串表示模型，供调试和测试时使用。
    def __repr__(self):
        return '<Role %r>' % self.name


class TempUser(db.Model):
    __tablename__ = 'temp_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)  # 创建索引，提升查询效率
    email = db.Column(db.String(100), unique=False)  # 邮箱
    phone = db.Column(db.String(11), unique=False)  # 手机号
    pwd = db.Column(db.String(100))  # 密码
    role_id = db.Column(db.Integer, db.ForeignKey('temp_roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username




