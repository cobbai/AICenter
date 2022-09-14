import os
import uuid

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, g, make_response, flash, \
    abort, current_app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from functools import wraps
from apps.article.form import *
from apps.article.model import *
from apps.auth.model import Permission
from bs4 import BeautifulSoup

article_bp = Blueprint("article", __name__, url_prefix="/article")


# """标签管理"""
# # 1.添加标签
# @article_bp.route("/article/tag_add/", methods=['GET', 'POST'])
# # @admin_auth
# def tag_add():
#     form = TagForm()
#     edit_flag = request.args.get("edit_flag")
#
#     if form.validate_on_submit():
#         data = form.data
#         tag = Tag(
#             name=data["name"]
#         )
#         db.session.add(tag)
#         db.session.commit()
#         flash('添加标签成功!', 'ok')
#         # 当前管理员添加了标签，添加操作日志
#         oplog = Oplog(
#             admin_id=session["admin_id"],
#             ip=request.remote_addr,
#             reason='添加标签:' + data['name']
#         )
#         db.session.add(oplog)
#         db.session.commit()
#         return redirect(url_for('article.tag_add'))
#     return render_template('movie/tag_add.html', form=form, edit_flag=edit_flag)
#
#
# # 2.标签列表
# @article_bp.route("/article/tag_list/", methods=["GET"])
# def tag_list():
#     page = int(request.args.get('page', 1))
#     auth_page = Tag.query.order_by(
#         Tag.addtime.desc()
#     ).paginate(page=page, per_page=2)
#     return render_template("movie/tag_list.html", auth_page=auth_page)
#
#
# # 3.删除标签
# @article_bp.route("/article/tag_del/", methods=["GET"])
# def tag_del():
#     id = request.args.get("id")
#     tag = Tag.query.filter_by(id=id).first_or_404()
#     db.session.delete(tag)
#     db.session.commit()
#     flash('删除标签成功!', 'warning')
#     return redirect(url_for("article.tag_list", page=1))
#
#
# # 4. 编辑标签
# @article_bp.route('/article/tag_edit/', methods=['GET', 'POST'])
# def tag_edit():
#     form = TagForm()
#     edit_flag = request.args.get("edit_flag")
#     id = request.args.get("id")
#     tag = Tag.query.get_or_404(id)
#     # 前台表单框里 展示目前状态
#     if request.method == "GET":
#         form.name.data = tag.name
#     # 修改提交表单后
#     if form.validate_on_submit():
#         data = form.data
#         # auth_count =Auth.query.filter_by(name=data["name"]).count()
#         # 验证名字是否修改
#         if tag.name == data["name"]:
#             flash("提交的新name已存在，请重新输入", "temp")
#             return redirect(url_for("article.tag_edit", id=id, edit_flag="edit"))
#         tag.name = data["name"]
#         db.session.add(tag)
#         db.session.commit()
#         flash('修改标签成功!', 'info')
#         return redirect(url_for('article.tag_edit', id=tag.id, edit_flag="edit"))
#     return render_template('movie/tag_add.html', form=form, edit_flag=edit_flag, id=id)


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


# 0.博客首页
@article_bp.route('/index', methods=['GET', 'POST'])
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
        return redirect(url_for('article.index'))

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


# 1.文章页
@article_bp.route('/article_page/<int:article_id>', methods=['GET', 'POST'])
def article_page(article_id):
    article = Article.query.get_or_404(article_id)
    # 评论
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(content=form.body.data,
                          article=article,
                          user=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('评论成功')
        return redirect(url_for('article.article_page', article_id=article_id))
    page = int(request.args.get('page', 1))
    pagination = article.comments.order_by(
        Comment.addtime.desc()
    ).paginate(page, per_page=5)

    return render_template('article/article_page.html', article=article, form=form, pagination=pagination)


# 2.编辑文章
@article_bp.route('/article_add', methods=['GET', 'POST'])
@login_required
@need_permission(Permission.WRITE)
def article_add():
    form = ArticlePostForm()
    edit = request.args.get('edit')
    article_id = request.args.get('article_id')

    # GET请求 并且 是编辑状态 才获取 article_id 进入编辑
    if request.method == "GET" and edit:
        article = Article.query.get_or_404(article_id)
        # 自己只能修改自己的文章
        if current_user != article.user and not current_user.can(Permission.ADMIN):
            abort(403)
        form.title.data = article.title
        # form.body.data = article.body_blob.decode('utf-8')
        form.body.data = article.body_html
        form.tag.data = article.tag_id

    if form.validate_on_submit():
        # 判断 body 是否空
        if not form.body.data:
            flash('内容不能为空', 'info')
            return render_template('article/article_add.html', form=form, edit=edit, article_id=article_id)
        if edit:
            # 旧文章修改
            article = Article.query.get_or_404(article_id)
            article.title = form.title.data
            # article.body = form.body.data
            # article.body_blob = form.body.data.encode('utf-8')
            article.body_html = form.body.data
            article.tag_id = form.tag.data
            db.session.commit()
        else:
            # 新文章入库
            article = Article(
                title=form.title.data,
                # body = form.body.data,
                # body_blob=form.body.data.encode('utf-8'),  # 富文本二进制保存
                body_html=form.body.data,  # 富文本保存html
                author_id=current_user.id,
                tag_id=form.tag.data,
            )
            db.session.add(article)
            db.session.commit()

        # 图片地址入库
        html = BeautifulSoup(form.body.data, "html.parser")
        for i in html.find_all("img"):
            image_exists = ArticleImage.query.filter_by(imgpath=i.get("src"), article_id=article.id).first()
            if not image_exists:
                # 图片相对地址保存数据库
                articleimage = ArticleImage(
                    imgpath=i.get("src"),
                    article_id=article.id,
                )
                db.session.add(articleimage)
        db.session.commit()
        flash('编辑新文章成功!', 'info')
        # TODO: 操作日志
        # oplog = Oplog(
        #     admin_id=session['admin_id'],
        #     ip=request.remote_addr,
        #     reason='添加电影:《' + movie.title + '》'
        # )
        # db.session.add(oplog)
        # db.session.commit()
        return redirect(url_for('article.article_page', article_id=int(article.id)))

    return render_template('article/article_add.html', form=form, edit=edit, article_id=article_id)


# 3.文章列表
@article_bp.route('/article_list', methods=['GET', 'POST'])
@login_required
@need_permission(Permission.WRITE)
def article_list():
    page = int(request.args.get('page', 1))
    # 不写join条件将默认使用外键关联
    auth_page = Article.query.order_by(
        Article.addtime.desc()
    ).paginate(page=page, per_page=5)
    return render_template("article/article_list.html", auth_page=auth_page)


# 4.删除文章
@article_bp.route("/article_del", methods=["GET"])
@login_required
@need_permission(Permission.WRITE)
def article_del():
    article_id = request.args.get("article_id")
    page = int(request.args.get('page', 1))

    article = Article.query.filter_by(id=article_id).first_or_404()
    # 删除文章中的图片
    articleimages = ArticleImage.query.filter_by(article_id=article_id).all()
    for i in articleimages:
        file_path = current_app.config['BASE_DIR'] + i.imgpath
        if os.path.exists(file_path):
            os.remove(file_path)
    ArticleImage.query.filter_by(article_id=article_id).delete()

    # 删除文章
    db.session.delete(article)
    db.session.commit()
    flash('删除文章成功!', 'warning')

    # # 将删除电影操作保存到操作日志列表
    # oplog = Oplog(
    #     admin_id=session['admin_id'],
    #     ip=request.remote_addr,
    #     reason='删除电影:《' + movie.title + '》'
    # )
    # db.session.add(oplog)
    # db.session.commit()
    return redirect(url_for("article.article_list", page=page))


# 5.图片上传
@article_bp.route("/picture", methods=["GET", "POST"])
@login_required
@need_permission(Permission.WRITE)
def picture():
    file = request.files.get("file")
    article_id = request.args.get("article_id")
    # TODO：云存储
    if file:
        # timce 自带图片验证，非图像传不上来
        # file_name = secure_filename(file.filename)
        file_name = uuid.uuid4().hex + "." + file.filename.split(".")[-1]
        relative_path = "upload/article_image/"
        file_path = os.path.join(current_app.config['STATIC_DIR'], relative_path)
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        file.save(file_path + file_name)

        location = url_for("static", filename=relative_path + file_name)
        return jsonify({"location": location})  # 返回 location 存放图片url
    return "ok"


# 1.所有人的博客
@article_bp.route('/show_all')
@login_required
def show_all():
    # make_response 创建响应对象，指定好 cookie 后重定向到首页
    resp = make_response(redirect(url_for('article.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


# 2.关注人的博客
@article_bp.route('/show_followed')
@login_required
def show_followed():
    # make_response 创建响应对象，指定好 cookie 后重定向到首页
    resp = make_response(redirect(url_for('article.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


# 1.评论列表
@article_bp.route("/comment_list", methods=["GET"])
@login_required
@need_permission(Permission.MODERATE)
def comment_list():
    page = int(request.args.get('page', 1))
    pagination = Comment.query.order_by(
        Comment.addtime.desc()
    ).paginate(page, per_page=5)
    return render_template("article/comment_list.html", pagination=pagination, page=page)


# 2.编辑评论
@article_bp.route("/comment_edit/<int:comment_id>", methods=["GET"])
@login_required
@need_permission(Permission.MODERATE)
def comment_edit(comment_id):
    status = request.args.get('status', 1)
    page = int(request.args.get('page', 1))
    comment = Comment.query.get_or_404(comment_id)
    if status:
        comment.disabled = True
    else:
        comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for("article.comment_list", page=page))


# """收藏管理"""
# # 1.收藏列表
# @article_bp.route("/article/moviecol_list/", methods=["GET"])
# def moviecol_list():
#     page = int(request.args.get('page', 1))
#     auth_page = Moviecol.query.join(Movie).join(User).filter(
#         Movie.id == Moviecol.movie_id,
#         User.id == Moviecol.user_id
#     ).order_by(
#         Moviecol.addtime.desc()
#     ).paginate(page=page, per_page=2)
#     return render_template("movie/moviecol.html", auth_page=auth_page)
#
#
# # 2.删除收藏
# @article_bp.route("/article/moviecol_del/", methods=["GET"])
# def moviecol_del():
#     id = request.args.get("id")
#     moviecol = Moviecol.query.filter_by(id=id).first_or_404()
#     db.session.delete(moviecol)
#     db.session.commit()
#     flash('删除收藏成功!', 'warning')
#     return redirect(url_for("article.moviecol", page=1))

