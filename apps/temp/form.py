from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, Regexp
from apps.temp.model import TempRole


class testForm(FlaskForm):
    name = StringField(
        label='昵称',
        validators=[
            DataRequired('请输入昵称!'),
        ],
        description='描述昵称',
    )
    email = StringField(
        label='邮箱',
        validators=[
            DataRequired('请输入邮箱!'),
            Email('邮箱格式不正确!')
        ],
        description='描述邮箱',
    )
    phone = StringField(
        label='手机',
        validators=[
            DataRequired('请输入手机号!'),
            Regexp("^1[35678]\d{9}$", message="手机格式不正确!")
        ],
        description='描述手机',
    )

    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired('请输入密码!')
        ],
        description='描述密码',
    )

    # role_id = SelectField(
    #     label="所属角色",
    #     validators=[
    #         DataRequired("请勾选所属角色!"),
    #     ],
    #     choices=[(i.id, i.name) for i in TempRole.query.all()],
    #     coerce=int,  # 默认情况下，key值是unicode。如果要使用int或其他数据类型，请在SkiForm类中使用coerce参数
    #     description='描述所属角色', )

    face = FileField(
        label='头像',
        validators=[
            # FileRequired(),
            FileAllowed(['jpg', 'png', 'gif'], message="图片格式错误")
        ],
        description='描述头像',
    )
    info = TextAreaField(
        label='简介',
        description='描述简介',
    )
    submit = SubmitField(
        label='保存修改',
    )