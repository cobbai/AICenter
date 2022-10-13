from flask import Blueprint, request, flash, redirect, url_for, render_template, abort
from flask_login import login_required, current_user

from apps.auth.form import *
from apps.auth.model import *
from apps.user.model import *
from functools import wraps

auth_bp = Blueprint("auth", __name__, url_prefix='/auth')


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


# TODO：搜索指定用户权限,修改
# 1.权限列表
@auth_bp.route("/auth_list/", methods=["GET"])
@login_required
@need_permission(Permission.ADMIN)
def auth_list():
    page = int(request.args.get('page', 1))
    auth_page = User.query.order_by(
        User.addtime.desc()
    ).paginate(page=page, per_page=5)
    return render_template("auth/auth_list.html", auth_page=auth_page)


# # 2.添加权限
# @auth_bp.route('/auth_add/', methods=['GET', 'POST'])
# @login_required
# def auth_add():
#     form = AuthForm()
#     edit_flag = request.args.get("edit_flag")
#     if form.validate_on_submit():
#         data = form.data
#         auth_count = Auth.query.filter_by(name=data['name']).count()
#         if auth_count == 1:
#             flash('该权限名已存在!请重新添加!', 'temp')
#             return redirect(url_for('auth.auth_add'))
#         auth = Auth(
#             name=data["name"],
#             url=data["url"]
#         )
#         db.session.add(auth)
#         db.session.commit()
#         flash("权限添加成功！", "info")
#     return render_template('auth/auth_edit.html', form=form, edit_flag=edit_flag)


# 3.删除权限
@auth_bp.route("/auth_del/", methods=["GET"])
@login_required
@need_permission(Permission.ADMIN)
def auth_del():
    page_num = 1
    if request.args.get("page"):
        page_num = request.args.get("page")
    id = request.args.get("id")
    user = User.query.filter_by(id=id).first_or_404()
    role = Role.query.filter_by(permissions=0).first()
    user.role_id = role.id
    db.session.add(user)
    db.session.commit()
    flash('删除权限成功!', 'info')
    return redirect(url_for("auth.auth_list", page=page_num))


# 4. 编辑权限
@auth_bp.route('/auth_edit/', methods=['GET', 'POST'])
@login_required
@need_permission(Permission.ADMIN)
def auth_edit():
    page = 1
    print(request.args)
    if request.args.get("page"):
        page = request.args.get("page")
    id = request.args.get("id")
    user = User.query.get_or_404(id)
    form = AuthForm(user)
    # 前台表单框里 展示目前状态
    if request.method == "GET":
        form.confirmed.data = user.confirmed
        form.role.data = user.role.id
    # 修改提交表单后
    if form.validate_on_submit():
        user.confirmed = form.confirmed.data
        user.role_id = form.role.data
        db.session.add(user)
        db.session.commit()
        flash('修改权限成功!', 'info')
        return redirect(url_for('auth.auth_edit', id=user.id, page=page))
    return render_template('auth/auth_edit.html', form=form, id=id, page=page)


"""标签管理"""
# 1.标签列表
@auth_bp.route("/tag_list/", methods=["GET"])
@login_required
@need_permission(Permission.ADMIN)
def tag_list():
    page = int(request.args.get('page', 1))
    tag_page = Tag.query.order_by(
        Tag.addtime.desc()
    ).paginate(page=page, per_page=3)
    return render_template("auth/tag_list.html", tag_page=tag_page)


# 2.删除标签
@auth_bp.route("/tag_del/", methods=["GET"])
@login_required
@need_permission(Permission.ADMIN)
def tag_del():
    tag_id = request.args.get("tag_id")
    tag = Tag.query.filter_by(id=tag_id).first_or_404()
    db.session.delete(tag)
    db.session.commit()
    flash('删除标签成功!', 'warning')
    return redirect(url_for("auth.tag_list", page=1))


# 3. 编辑标签
@auth_bp.route("/tag_add/", methods=['GET', 'POST'])
@login_required
@need_permission(Permission.ADMIN)
def tag_add():
    form = TagForm()
    edit = request.args.get("edit")
    tag_id = request.args.get("tag_id")

    # GET请求 并且 是编辑状态 才获取 tag_id 进入编辑
    if request.method == "GET" and edit:
        tag = Tag.query.get_or_404(tag_id)
        form.new_tag.data = tag.tag_name

    if form.validate_on_submit():
        # 判断 body 是否空
        if not form.new_tag.data:
            flash('内容不能为空', 'info')
            return render_template('auth/tag_add.html', form=form, edit=edit, tag_id=tag_id)
        if edit:
            # 旧标签修改
            tag = Tag.query.get_or_404(tag_id)
            tag.tag_name = form.new_tag.data
            tag.tag_name_en = form.new_tag_en.data
        else:
            # 新标签入库
            tag = Tag(
                tag_name=form.new_tag.data,
                tag_name_en=form.new_tag_en.data,
            )

        db.session.add(tag)
        db.session.commit()
        flash('修改标签成功!', 'info')
        return redirect(url_for('auth.tag_list'))

    return render_template('auth/tag_add.html', form=form, edit=edit, tag_id=tag_id)
