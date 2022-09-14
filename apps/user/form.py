from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, SelectField, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo, Email, Regexp
from apps.user.model import User
import re


"""用户注册表单"""
class RegistForm(FlaskForm):
    register_name = StringField(
        label="名称",
        validators=[
            DataRequired("请输入昵称!")
        ],
        description="请输入昵称",
        render_kw={
            "class": "form-control",
            "placeholder": "Name (displayed)",
            # "required": False,  # 不显示浏览器自带的提示
            "id": "register-name"
        }
    )

    register_email = StringField(
        label="邮箱",
        validators=[
            DataRequired("请输入邮箱!"),
            Email("邮箱格式不正确!"),  # pip install email_validator -i https://pypi.douban.com/simple/
        ],
        description="请输入邮箱",
        render_kw={
            "class": "form-control",
            "placeholder": "Email address",
            # "required": False,  # 不显示浏览器自带的提示
            "id": "register-email",
            "type": "email"
        }
    )

    # register_phone = StringField(
    #     label="手机",
    #     validators=[
    #         DataRequired("请输入手机号!"),
    #         Regexp("^1[35678]\d{9}$", message="手机格式不正确!"),
    #     ],
    #     description="手机",
    #     render_kw={
    #         "class": "form-control",
    #         "placeholder": "Phone",
    #         # "required": False,  # 不显示浏览器自带的提示
    #         "id": "register-phone"
    #     }
    # )

    register_pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired('请输入密码!'),
            Length(min=7, message='密码至少7个字符')
        ],
        description='密码',
        render_kw={
            "class": "form-control",
            "placeholder": "Password (min 7 chars)",
            # "required": False,  # 不显示浏览器自带的提示
            "id": "register-pwd",
            "autoComplete": "true",

            # validator 验证信息
            "title": "注册密码",  # en.json 中的 %s占位符
            "minlength": "7",
        }
    )

    register_repwd = PasswordField(
        label="确认密码",
        validators=[
            DataRequired('请输入密码!'),
            EqualTo('register_pwd', '两次密码不一致!')
        ],
        description='确认密码',
        render_kw={
            "class": "form-control",
            "placeholder": "Verify password",
            # "required": False,  # 不显示浏览器自带的提示
            "id": "register-repwd",
            "autoComplete": "true",

            # validator 验证
            "data-v-equal": "#register-pwd",
        }
    )

    register_submit = SubmitField(
        label='注册',
        render_kw={
            "class": "btn btn-dark",
            "id": "register-submit",
            "style": "padding: 0px 24px; "
                     "border-radius: 20px; "
                     "height: 36px; "
                     "align-items: center; "
                     "background-color: rgb(32, 33, 36);"
        }
    )

    # 自定义验证：validate_<fieldname>
    def validate_register_name(self, field):  # data 是表单返回的数据
        user_cnt = User.query.filter_by(name=field.data).count()
        if user_cnt == 1:
            raise ValidationError("昵称已存在!")

    def validate_register_email(self, field):
        email_cnt = User.query.filter_by(email=field.data.lower()).count()
        if email_cnt == 1:
            raise ValidationError("邮箱已存在!")

    # def validate_register_phone(self, field):
    #     phone_cnt = User.query.filter_by(phone=field.data).count()
    #     if phone_cnt == 1:
    #         raise ValidationError("手机已存在!")


"""登录表单"""
class LoginForm(FlaskForm):
    login_name = StringField(
        label="账号",
        validators=[
            DataRequired(message="请输入账号!")
        ],
        description="账号",
        render_kw={
            "class": "form-control",
            "placeholder": "Name",
            # "required": False,  # 不显示浏览器自带的提示
            "id": "login-name"
        }
    )
    login_pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired("请输入密码!"),
            Length(min=7, message='密码至少7个字符')
        ],
        description="密码",
        render_kw={
            "class": "form-control",
            "placeholder": "Password",
            # "required": False,
            "id": "login-pwd",
            "autoComplete": "true",

            # validator 验证
            "minlength": "7",
        }
    )
    login_submit = SubmitField(
        label='登录',
        render_kw={
            "class": "btn btn-dark",
            "id": "login-submit",
            "style": "padding: 0px 24px; "
                     "border-radius: 20px; "
                     "height: 36px; "
                     "align-items: center; "
                     "background-color: rgb(32, 33, 36);"
        }
    )


"""用户中心表单"""
class UserdetailForm(FlaskForm):
    name = StringField(
        label='昵称',
        validators=[
            DataRequired('请输入昵称!'),
        ],
        description='昵称',
    )
    email = StringField(
        label='邮箱',
        validators=[
            DataRequired('请输入邮箱!'),
            Email('邮箱格式不正确!')
        ],
        description='邮箱',
    )
    # phone = StringField(
    #     label='手机',
    #     validators=[
    #         DataRequired('请输入手机号!'),
    #         Regexp("^1[35678]\d{9}$", message="手机格式不正确!")
    #     ],
    #     description='手机',
    # )
    face = FileField(
        label='头像',
        validators=[
            # FileRequired(),
            FileAllowed(['jpg', 'png', 'gif', 'jpeg'], message="图片格式错误")
        ],
        description='头像',
    )
    info = TextAreaField(
        label='简介',
        description='简介',
    )
    location = StringField(
        label='所在地',
        validators=[Length(0, 64)]
    )
    real_name = StringField(
        label='真实姓名',
        validators=[Length(0, 64)]
    )
    submit = SubmitField(
        label='保存修改',
    )


"""重设密码表单"""
class PwdForm(FlaskForm):
    old_pwd = PasswordField(
        label='旧密码',
        validators=[
            DataRequired('请输入旧密码!'),
        ],
        description='旧密码',
    )
    new_pwd = PasswordField(
        label='新密码',
        validators=[
            DataRequired('请输入新密码!'),
        ],
        description='新密码',
    )
    submit = SubmitField(
        label='修改密码',
    )


"""重设密码表单"""
class PasswordResetRequestForm(FlaskForm):
    email = StringField(
        label='邮箱',
        validators=[
            DataRequired('请输入邮箱!'),
            Email('邮箱格式不正确!')
        ],
        description='邮箱',
    )
    submit = SubmitField(
        label='发送邮件确认',
    )


class PasswordResetForm(FlaskForm):
    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired('请输入密码!')
        ],
        description='密码',
    )

    repwd = PasswordField(
        label="确认密码",
        validators=[
            DataRequired('请输入密码!'),
            EqualTo('pwd', '两次密码输入不一致!')
        ],
        description='确认密码',
    )

    submit = SubmitField(
        label='提交',
    )


"""重设邮箱表单"""
class ChangeEmailForm(FlaskForm):
    email = StringField(
        label='新邮箱',
        validators=[
            DataRequired('请输入邮箱!'),
            Email('邮箱格式不正确!')
        ],
        description='新邮箱',
    )
    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired('请输入密码!')
        ],
        description='密码',
    )
    submit = SubmitField(
        label='提交',
    )

    def validate_email(self, field):
        email_cnt = User.query.filter_by(email=field.data.lower()).count()
        if email_cnt == 1:
            raise ValidationError("邮箱已存在!")
