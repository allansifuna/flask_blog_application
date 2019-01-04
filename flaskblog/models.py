from datetime import datetime
from flask import current_app
from flaskblog import db, login_manager
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# from flask_dance.contrib import make_twitter_blueprint


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    is_auth = db.Column(db.Integer, nullable=False, default=0)
    is_online = db.Column(db.String(20), nullable=False, default="Offline")
    user_role = db.Column(db.String(20), nullable=False, default="User")
    email = db.Column(db.String(250), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default="default_image.jpg")
    password = db.Column(db.String(20), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    comment = db.relationship('Comment', backref='comment_author', lazy=True)

    def get_reset_token(self, expires_sec=18000):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except Exception as e:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}','{self.password}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    is_auth = db.Column(db.Integer, nullable=False, default=0)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='comment', lazy=True)

    def __repr__(self):
        return f"Post('{self.title}','{self.date_posted}')"


class Subscribers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return f"Subscribers({self.email})"


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(600), nullable=False)

    def __repr__(self):
        return f"Comment({self.post_id},{self.user_id},{self.content})"
