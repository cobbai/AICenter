from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo, Email, Regexp
from apps.auth.model import Role


'''权限表单'''
class AuthForm(FlaskForm):
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    submit = SubmitField(
        label='提交',
    )

    def __init__(self, user, *args, **kwargs):
        super(AuthForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.role_name) for role in Role.query.order_by(Role.permissions.asc()).all()]
        self.user = user

# '''角色表单'''
# class RoleForm(FlaskForm):
#     name = StringField(
#         label="角色名称",
#         validators=[
#             DataRequired("请输入角色名称")
#         ],
#         description="角色名称",
#     )
#
#     auths = SelectMultipleField(
#         label="权限列表",
#         validators=[
#             DataRequired("请勾选操作权限!")
#         ],
#         choices=[(i.id, i.name) for i in Auth.query.all()],  # import db，存在上下文问题。需要 app.app_context().push()
#         coerce=int,  #  (i.id, i.name)元组中的标识符是id，需要是整数，因此coerce=int
#         description='权限列表',
#     )
#     submit = SubmitField(
#         label='提交',
#     )


# '''管理员注册表单'''
# class AdminForm(FlaskForm):
#     name =StringField(
#         label="管理员名称",
#         validators=[
#             DataRequired("请输入管理员名称")
#         ],
#         description="管理员名称",
#     )
#     pwd = PasswordField(
#         label='管理员密码',
#         validators=[
#             DataRequired('请输入管理员密码!'),
#             Length(min=6, max=12, message="长度必须6-12")
#         ],
#         description='管理员密码',
#     )
#     repwd = PasswordField(
#         label='管理员密码',
#         validators=[
#             DataRequired('请输入管理员密码!'),
#             Length(min=6, max=12, message="长度必须6-12"),
#             EqualTo("pwd", message='两次密码输入不一致!')
#         ],
#         description='管理员密码', )
#     role_id = SelectField(
#         label="所属角色",
#         validators=[
#             DataRequired("请勾选所属角色!"),
#                     ],
#         choices=[(i.id, i.name) for i in Role.query.all()],
#         coerce=int,  # 默认情况下，key值是unicode。如果要使用int或其他数据类型
#         description='所属角色',)
#     submit = SubmitField(label='提交',)