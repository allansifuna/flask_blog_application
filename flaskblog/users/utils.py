import os
import secrets
from PIL import Image
from flask import current_app, render_template
from flask_mail import Message
from flaskblog import mail


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static\\profile_pic', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply.sifuna@gmail.com', recipients=[user.email])
    root = 'http://192.168.45.182:5000/reset_password/' + token
    msg.html = render_template('reset_email.html', root=root, _external=True)
    mail.send(msg)


def send_subscription_email(users):
    for user in users:
        msg = Message('Subscription at Flask blog', sender='noreply.sifuna@gmail.com', recipients=[user.email])
        msg.html = render_template('reset_email.html', _external=True)
        mail.send(msg)


def send_subscription_confirm_email(user):
    msg = Message('Subscription at Flask blog', sender='noreply.sifuna@gmail.com', recipients=[user.email])
    msg.html = render_template('reset_email.html', _external=True)
    mail.send(msg)


def send_register_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply.sifuna@gmail.com', recipients=[user.email])
    root = 'http://192.168.45.182:5000/authenticate/' + token
    msg.html = render_template('register_email.html', root=root, _external=True)
    mail.send(msg)
