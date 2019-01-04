import os


class Config:
    SECRET_KEY = '52eaf892e503af6001950ab4f7ef2459'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('email')
    MAIL_PASSWORD = os.environ.get('Password')
