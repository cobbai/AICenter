from apps import db
from datetime import datetime
import hashlib
from markdown import markdown
import bleach


# 博客
class Blog(db.Model):
    __tablename__ = 'blog'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # on_changed_body() 函数把body字段中的文本渲染成HTML格式，将结果保存在body_html中，
    # 自动且高效地完成Markdown 文本到HTML 的转换。
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        # 3、linkify() 把纯文本中的URL 转换成合适的<a> 链接
        target.body_html = bleach.linkify(
            # 2、clean() 函数删除所有不在 allowed_tags 中的标签
            bleach.clean(
                # 1、markdown() 函数初步把Markdown 文本转换成HTML。
                markdown(value, output_format='html'),
                tags=allowed_tags,
                strip=True
            )
        )


# SQLAlchemy“set”事件的监听程序，只要body字段设了新值，on_changed_body()就会自动被调用
db.event.listen(Blog.body, 'set', Blog.on_changed_body)

# 文章
class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    title = db.Column(db.String(255))  # 文章名
    # body_blob = db.Column(db.BLOB)  # 富文本包含图片和文字，用二进制保存
    # body = db.Column(db.Text)  # 文章内容
    body_html = db.Column(db.Text)  # html文章内容
    star = db.Column(db.SmallInteger, default=0)  # 星级
    read_num = db.Column(db.BigInteger, default=0)  # 浏览数
    comment_num = db.Column(db.BigInteger, default=0)  # 评论数
    addtime = db.Column(db.DateTime, index=True, default=datetime.utcnow)  # 添加时间
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))  # Article 下的 Tag 用 tag

    comments = db.relationship('Comment', backref='article', lazy='dynamic')  # 评论外键关系关联
    articlecols = db.relationship('Articlecol', backref='article')  # 收藏外键关系关联
    images = db.relationship('ArticleImage', backref='article')

    def __repr__(self):
        return '<Article %r>' % self.title

#     @staticmethod
#     def on_changed_body(target, value, oldvalue, initiator):
#         allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
#                         'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
#                         'h1', 'h2', 'h3', 'p']
#         target.body_html = bleach.linkify(
#             bleach.clean(
#                 markdown(value, output_format='html'),
#                 tags=allowed_tags,
#                 strip=True
#             )
#         )
#
#
# db.event.listen(Article.body, 'set', Article.on_changed_body)


# 图片
class ArticleImage(db.Model):
    __tablename__ = 'articleimage'
    id = db.Column(db.Integer, primary_key=True)
    imgpath = db.Column(db.Text)  # 图片相对路径
    show = db.Column(db.Boolean, default=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))  # 所属文章
    addtime = db.Column(db.DateTime, index=True, default=datetime.utcnow)  # 添加时间

    def __repr__(self):
        return '<ArticleImage %r>' % self.id


# 评论
class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    content = db.Column(db.Text)  # 评论内容
    content_html = db.Column(db.Text)  # 评论内容
    disabled = db.Column(db.Boolean)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))  # 所属文章
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属用户
    addtime = db.Column(db.DateTime, index=True, default=datetime.utcnow)  # 评论时间

    def __repr__(self):
        return '<Comment %r>' % self.id

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.content_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))


db.event.listen(Comment.content, 'set', Comment.on_changed_body)


# 收藏文章
class Articlecol(db.Model):
    __tablename__ = 'articlecol'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))  # 所属电影
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属用户
    addtime = db.Column(db.DateTime, index=True, default=datetime.utcnow)  # 添加时间

    def __repr__(self):
        return '<Articlecol %r>' % self.id