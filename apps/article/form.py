from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_pagedown.fields import PageDownField
from wtforms import StringField, PasswordField, SubmitField, SelectField, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo, Email, Regexp
from apps.auth.model import Tag


class ArticlePostForm(FlaskForm):
    title = StringField("文章标题", validators=[DataRequired()])
    # body = PageDownField("文章正文", validators=[DataRequired()])
    body = TextAreaField(
        "文章正文",
        # validators=[DataRequired()],  # data required 报错，放在路由函数中判断是否空
        render_kw={"class": "content_area"}  # render_kw 控制渲染内容的属性
    )
    tag = SelectField(
        "文章分类",
        coerce=int,
    )
    submit = SubmitField('提交')

    def __init__(self, *args, **kwargs):
        super(ArticlePostForm, self).__init__(*args, **kwargs)
        self.tag.choices = [(tag.id, tag.tag_name) for tag in Tag.query.order_by(Tag.tag_name.asc()).all()]


class BlogPostForm(FlaskForm):
    body = PageDownField("有什么想法？", validators=[DataRequired()])  # PageDownField() Markdown 富文本编辑器
    submit = SubmitField('提交')


class CommentForm(FlaskForm):
    body = StringField("评论内容", validators=[DataRequired()])  # PageDownField() Markdown 富文本编辑器
    submit = SubmitField('提交')