from flask_mail import Message
from apps import mail
from threading import Thread
from flask import render_template, current_app


def send_async_email(app, msg):
    # 异步线程需要同步应用上下文
    with app.app_context():
        mail.send(msg)


# recipients：收件人地址
# subject：主题
# mail_content：渲染邮件正文的模板
def send_email(recipients, subject, mail_content, **kwargs):
    app = current_app._get_current_object()
    FLASKY_MAIL_SUBJECT_PREFIX = '[Cobb_AIweb]'
    FLASKY_MAIL_SENDER = app.config["MAIL_USERNAME"]
    msg = Message(FLASKY_MAIL_SUBJECT_PREFIX + subject, sender=FLASKY_MAIL_SENDER, recipients=[recipients])
    # msg.body = mail_content + str(kwargs["user"].name)

    # user的name和token通过可变参数传入文本模板
    # _external=True 使url_for()生成完整的链接（包括协议（http:// 或https://）、主机名和端口。）
    msg.body = render_template(mail_content + '.txt', **kwargs)
    # TODO: msg.html = render_template(template + '.html', **kwargs)

    # 异步发送邮件
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr