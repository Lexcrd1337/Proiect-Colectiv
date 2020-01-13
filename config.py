import os


class Config(object):
    DEBUG = False
    TESTING = False
    MAIL_USERNAME = os.environ['EMAIL_USER']
    MAIL_PASSWORD = os.environ['EMAIL_PASSWORD']
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_PORT = 465
    MAIL_SERVER = 'smtp.gmail.com'
    SECRET_KEY = os.environ['SECRET_KEY']
    CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    UPLOAD_PROPOSALS_FOLDER = os.environ['UPLOAD_PROPOSALS_FOLDER']
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
