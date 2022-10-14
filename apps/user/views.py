import os
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, g, make_response, abort, \
    flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash  # 密码加盐
from flask_login import login_required, logout_user, login_user, current_user

from apps.article.form import BlogPostForm
from apps.article.model import Blog
from apps.user.model import *
from apps.user.form import *
from apps.user.email import *
from apps.auth.model import *
from functools import wraps
import uuid

user_bp = Blueprint("user", __name__, url_prefix='/user')


# 模板中使用权限变量（针对蓝图）
@user_bp.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)


"""
def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("被装饰的函数 增加新功能")
        return func(*args, **kwargs)
    return wrapper
    
# 1、decorator 要返回 一个函数
# 2、将 被装饰的函数func 作为 decorator 的参数
# 3、func被装饰后 __name__会变为 wrapper
# 4、@wraps 使 __name__ 不变
# 5、当你使用@my_decorator语法时，你是在应用一个以单个函数作为参数的一个包裹函数 （func：被装饰的函数 作为参数）
"""


# 通过装饰器传参数，让装饰器自己接受参数
def need_permission(perm):
    # 自定义装饰器：角色权限访问控制装饰器
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.can(perm):
                abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator


# 钩子函数: 请求前执行，应用再全局蓝图上
@user_bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
    # 登录了 and 没confirmed and 访问的不是user_bp and 不是静态文件的请求
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.blueprint != 'user' \
            and request.endpoint != 'static' :
        flash("请前往邮箱，确认注册链接")
        return redirect(url_for('user.user_unconfirmed'))


# 未确认注册链接的用户限制在 user_unconfirmed.html
@user_bp.route('/unconfirmed/')
def user_unconfirmed():
    # print("current_user.is_anonymous", current_user.is_anonymous)
    # 未注册的匿名用户 or confirmed的用户 直接去首页
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('user.index'))
    return render_template('user/user_unconfirmed.html')


# 0.初始化数据库
@user_bp.route("/init_db/")
def init_db():
    Role.insert_roles()
    print("数据库初始化：")
    print(Role.query.all())
    return redirect(url_for('user.index'))


# # 1.用户注册
# @user_bp.route("/add", methods=["GET", "POST"])
# def user_add():
#     form = RegistForm()
#     if form.validate_on_submit():
#         user = User(
#             name=form.register_name.data,
#             email=form.register_email.data.lower(),
#             phone=form.register_phone.data,
#             pwd=generate_password_hash(form.register_pwd.data),  # 加盐用户的密码
#             uuid=uuid.uuid4().hex  # 生成用户的唯一标志符
#         )
#         db.session.add(user)
#         db.session.commit()
#
#         # 发送登录邮件 前commit()数据库才能生成id
#         token = user.generate_confirmation_token()  # 对当前注册用户生成签名令牌
#         send_email(user.email, '确认注册邮件', 'email/confirm', user=user, token=token)
#
#         flash('已发送注册链接至您的邮箱，请前去确认!', 'warning')
#         return redirect(url_for('user.index'))
#     return render_template("user/user_add.html", form=form)


# 0.博客首页
@user_bp.route('/index/', methods=['GET', 'POST'])
def index():
    page = int(request.args.get('page', 1))
    form = BlogPostForm()
    # 匿名用户可以看，但不能添加博客
    if not current_user.is_anonymous and form.validate_on_submit():
        blog = Blog(
            body=form.body.data,
            user=current_user._get_current_object(),  # current_user只是用户对象的轻度包装。_get_current_object()返回数据库需要的真正用户对象
        )
        db.session.add(blog)
        db.session.commit()
        return redirect(url_for('user.index'))

    # 显示关注人的博客
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_blogs  # Model里的property方法
    else:
        query = Blog.query

    blog_page = query.order_by(
        Blog.timestamp.desc()
    ).paginate(page=page, per_page=5)
    blogs = blog_page.items  # 返回分页后的项目
    return render_template("index.html", form=form, blogs=blogs, blog_page=blog_page)


# 邮件确认链接生成
@user_bp.route('/confirm/<token>/')
@login_required
def user_confirm(token):
    if current_user.confirmed:
        return redirect(url_for('user.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('您已注册成功！', 'info')
    else:
        flash('注册链接无效或过期', 'warning')
    return redirect(url_for('user.index'))


# 重新发送确认链接
@user_bp.route('/confirm/')
@login_required
def user_resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, '确认注册邮件', 'email/confirm', user=current_user, token=token)
    flash('重新向您的邮箱发送了注册链接')
    return redirect(url_for('user.index'))


# 2.用户登录
@user_bp.route('/login/', methods=['GET', 'POST'])
def user_login():
    loginform = LoginForm()
    registerform = RegistForm()
    # 登录
    if loginform.login_submit.data and loginform.validate_on_submit():
        user = User.query.filter_by(name=loginform.login_name.data).first()
        if not user:
            flash("没有此用户名!", "temp")
            return redirect(url_for("user.user_login"))
        if not user.check_pwd(pwd=loginform.login_pwd.data):
            flash("密码错误!", "temp")
            return redirect(url_for("user.user_login"))

        # # 登录成功 保存session
        # session["user"] = user.name
        # session["user_id"] = user.id
        login_user(user)  # flask_login

        # 登录操作存入登录日志
        userlog = Userlog(
            user_id=current_user.id,
            ip=request.remote_addr,  # 获取IP
        )
        db.session.add(userlog)
        db.session.commit()

        return redirect(url_for("user.user_center"))
    # 注册
    elif registerform.register_submit.data and registerform.validate_on_submit():
        user = User(
            name=registerform.register_name.data,
            email=registerform.register_email.data.lower(),
            # phone=registerform.register_phone.data,
            pwd=generate_password_hash(registerform.register_pwd.data),  # 加盐用户的密码
            uuid=uuid.uuid4().hex  # 生成用户的唯一标志符
        )
        db.session.add(user)
        db.session.commit()

        # 发送登录邮件 前commit()数据库才能生成id
        token = user.generate_confirmation_token()  # 对当前注册用户生成签名令牌
        send_email(user.email, '确认注册邮件', 'email/confirm', user=user, token=token)
        # 登录
        login_user(user)
        flash('已发送注册链接至您的邮箱，请前去确认!', 'warning')
        #  未验证邮箱的用户会先出发钩子函数
        return redirect(url_for('user.index'))
    return render_template("user/user_login.html", loginform=loginform, registerform=registerform)


# 3.用户登出
@user_bp.route('/logout/')
@login_required
def user_logout():
    logout_user()  # flask_login
    return redirect(url_for('user.index'))


# 4.用户中心
@user_bp.route('/center/', methods=['GET', 'POST'])
@login_required
@need_permission(Permission.WRITE)
def user_center():
    form = UserdetailForm()
    user = User.query.get_or_404(current_user.id)  # 用户名不存在则404
    blogs = user.blogs.order_by(Blog.timestamp.desc()).all()  # 通过关系获得user的blogs，不加lazy='dynamic'排序order_by会报错
    # 前台展示用户当前信息
    if request.method == "GET":
        form.name.data = user.name
        form.email.data = user.email
        # form.phone.data = user.phone
        form.info.data = user.info
        form.location.data = user.location
        form.real_name.data = user.real_name

    # 修改信息
    if form.validate_on_submit():
        # 如果信息在库内已存在 + 提交的信息不是原信息，则修改失败
        # TODO:修改姓名按钮 + 用验证码修改手机号
        # user_name = User.query.filter_by(name=form.name.data).count()
        # if user_name == 1 and form.name.data == user.name:
        #     flash("用户昵称已存在,请重新输入!", "error")
        #     return redirect(url_for('user.user_center'))
        # user_email = User.query.filter_by(email=form.email.data.lower()).count()
        # if user_email == 1 and form.email.data.lower() == user.email:
        #     flash("用户邮箱已存在,请重新输入!", "error")
        #     return redirect(url_for('user.user_center'))
        # user_phone = User.query.filter_by(phone=form.phone.data).count()
        # if user_phone == 1 and form.phone.data == user.phone:
        #     flash("用户手机已存在,请重新输入!", "error")
        #     return redirect(url_for('user.user_center'))

        # 修改头像
        if form.face.data:
            face_name = secure_filename(form.face.data.filename)  # secure_filename规范化文件名
            form.face.data.save(os.path.join(current_app.config['UPLOAD_DIR'] + "\\avatar", face_name))
            user.face = os.path.join("upload/", face_name)  # 库里记录 static 下的路径

        # user.name = form.name.data
        # user.email = form.email.data
        # user.phone = form.phone.data
        user.info = form.info.data
        user.location = form.location.data
        user.real_name = form.real_name.data
        db.session.add(user)
        db.session.commit()
        flash('修改资料成功!', 'info')
        return redirect(url_for('user.user_center'))
    return render_template("user/user_center.html", form=form, user=user, blogs=blogs)


# 5.修改密码
@user_bp.route("/pwd/", methods=["GET", "POST"])
@login_required
def user_pwd():
    form = PwdForm()
    user = User.query.filter_by(id=current_user.id).first()
    if form.validate_on_submit():
        if not user.check_pwd(form.old_pwd.data):
            flash('旧密码错误!请重新输入!', 'temp')
            return redirect(url_for('user.user_pwd'))
        user.pwd = generate_password_hash(form.new_pwd.data)
        db.session.add(user)
        db.session.commit()
        flash('修改密码成功!请重新登录', 'info')
        return redirect(url_for('user.user_logout'))
    return render_template("user/user_pwd.html", form=form)


# 6.重设密码
@user_bp.route("/reset_pwd/", methods=["GET", "POST"])
def user_reset_pwd_request():
    # 匿名用户才进重设密码
    if not current_user.is_anonymous:
        return redirect(url_for('user.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, '重设密码', '/email/reset_password', user=user, token=token)
            flash('已向您的邮箱发送重设密码链接！')
        else:
            flash("请先注册！")
        return redirect(url_for('user.user_login'))
    return render_template('user/user_reset_pwd.html', form=form)


@user_bp.route("/reset_pwd/<token>/", methods=["GET", "POST"])
def user_reset_pwd(token):
    # 匿名用户才进重设密码
    if not current_user.is_anonymous:
        return redirect(url_for('user.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        # 因为现在是匿名用户，所以不能用 current_user 获取 User 函数
        # @staticmethod 不用实例化User，直接访问User.reset_password()
        if User.reset_password(token, generate_password_hash(form.pwd.data)):
            db.session.commit()
            flash('重设密码成功')
            return redirect(url_for('user.user_login'))
        else:
            return redirect(url_for('user.index'))
    return render_template('user/user_reset_pwd.html', form=form)


# 7.重设邮件
@user_bp.route("/change_email/", methods=["GET", "POST"])
@login_required
def user_change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.check_pwd(form.pwd.data):
            new_email = form.email.data.lower()
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, '修改邮箱', '/email/change_email', user=current_user, token=token)
            flash('修改邮箱链接已发送至您的新邮箱')
            return redirect(url_for('user.index'))
        else:
            flash('无效的邮箱')
    return render_template("user/user_reset_pwd.html", form=form)


@user_bp.route("/change_email/<token>/")
@login_required
def user_change_email(token):
    if current_user.change_email(token):
        db.session.commit()
        flash('邮箱已更新')
    else:
        flash('更新邮箱请求无效')
    return redirect(url_for('user.index'))


# 7.用户资料
@user_bp.route("/user_detail/<uid>/", methods=["GET", "POST"])
def user_detail(uid):
    user = User.query.get_or_404(uid)
    return render_template("user/user_detail.html", user=user)


# 8.关注用户
@user_bp.route("/follow/<uid>/", methods=["GET", "POST"])
@login_required
@need_permission(Permission.FOLLOW)
def follow(uid):
    user = User.query.filter_by(id=uid).first()
    if not user:
        flash('无效用户!', 'info')
        return redirect(url_for('user.index'))
    if current_user.is_following(user):
        flash('您已经关注此用户!', 'info')
        return redirect(url_for('user.user_detail', uid=uid))
    current_user.follow(user)
    flash('您关注了用户：' + user.name, 'info')
    return redirect(url_for('user.user_detail', uid=uid))


# 9.取消关注
@user_bp.route("/unfollow/<uid>/", methods=["GET", "POST"])
@login_required
@need_permission(Permission.FOLLOW)
def unfollow(uid):
    user = User.query.filter_by(id=uid).first()
    if not user:
        flash('无效用户!', 'info')
        return redirect(url_for('user.index'))
    if not current_user.is_following(user):
        flash('您未关注此用户!', 'info')
        return redirect(url_for('user.user_detail', uid=uid))
    current_user.unfollow(user)
    flash('您取消关注了用户：' + user.name, 'info')
    return redirect(url_for('user.user_detail', uid=uid))


# 10.关注了
@user_bp.route("/followers/<uid>/", methods=["GET", "POST"])
def followers(uid):
    user = User.query.filter_by(id=uid).first()
    if not user:
        flash('无效用户!', 'info')
        return redirect(url_for('user.index'))
    page = request.args.get('page', 1)
    pagination = user.followers.paginate(page, per_page=5)
    # pagination.items 取出每页的所有项目
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('user/followers.html',
                           user=user, title="Followers of",
                           pagination=pagination,
                           endpoint='.followers',
                           follows=follows)


# 10.被关注
@user_bp.route("/followed_by/<uid>/", methods=["GET", "POST"])
def followed_by(uid):
    user = User.query.filter_by(id=uid).first()
    if not user:
        flash('无效用户!', 'info')
        return redirect(url_for('user.index'))
    page = request.args.get('page', 1)
    pagination = user.followed.paginate(page, per_page=5)
    # pagination.items 取出每页的所有项目
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('user/followers.html',
                           user=user, title="Followed of",
                           pagination=pagination,
                           endpoint='.followed_by',
                           follows=follows)

