import os
import app

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
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://giaaqdpgntyuod:a16a0b06413976fa27efd603a0852578650aeb052969da69e4f348ad14956291@ec2-3-220-86-239.compute-1.amazonaws.com:5432/dbvci5jlai3sr1'
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
