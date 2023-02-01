from apps import db
from datetime import datetime
from werkzeug.security import check_password_hash


"""
用户角色     |         权限                           |    说明
匿名        |          无                            |    对应只读权限；这是未登录的未知用户
用户        |    FOLLOW、COMMENT、WRITE              |    具有发布文章、发表评论和关注其他用户的权限；这是新用户的默认角色
模型订购用户  |    FOLLOW、COMMENT、WRITE、MODEL       |
协管员       |    FOLLOW、COMMENT、WRITE、MODERATE    |    增加管理其他用户所发表评论的权限
管理员       |            63                         |   具有所有权限，包括修改其他用户所属角色的权限
"""


class Permission:
    # 使用2的幂表示权限
    FOLLOW = 1  # 关注
    COMMENT = 2  # 评论
    WRITE = 4  # 发表文章
    MODEL = 8  # 订阅模型
    MODERATE = 16  # 管理他人发表文章
    ADMIN = 32  # 管理员


# 角色创建
class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    role_name = db.Column(db.String(64), unique=True)  # 角色名
    permissions = db.Column(db.Integer, default=0)  # 角色的权限:
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 创建时间

    # lazy默认值select。query().first()的时候会直接查出对象。dynamic查出变量，可以继续filter_by()
    user = db.relationship('User', backref='role', lazy='dynamic')  # "一"这端。

    def __repr__(self):
        return '<Role %r>' % self.name

    def has_permission(self, perm):
        # 按位与&：参与运算的两个值,如果二进制的两个相应位都为1,则该位的结果为1,否则为0。
        # 检查 权限组合 是否包含指定的 单独权限。
        return self.permissions & perm == perm

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    # 更新角色权限、创建新角色时调用该静态方法
    @staticmethod
    def insert_roles():
        roles = {
            # 若更新角色，只需更新这个字典
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Modeler': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODEL],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT,
                          Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT,
                              Permission.WRITE, Permission.MODEL, Permission.MODERATE,
                              Permission.ADMIN],
        }
        for r in roles:
            role = Role.query.filter_by(role_name=r).first()
            if role is None:
                role = Role(role_name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            db.session.add(role)
        db.session.commit()


# 文章标签
class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    tag_name = db.Column(db.String(100), unique=True)  # 标签名
    tag_name_en = db.Column(db.String(100), unique=True)  # 标签名
    source = db.Column(db.String(100))  # 来源
    addtime = db.Column(db.DateTime, index=True, default=datetime.utcnow)  # 标签的添加时间

    articles = db.relationship('Article', backref='tag')  # Tag 下的 Article 用 articles

    def __repr__(self):
        return '<Tag %r>' % self.tag_name