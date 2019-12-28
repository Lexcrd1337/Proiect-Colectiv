import os
from flask import Flask, render_template
from flask_login import LoginManager
from extensions import db

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])

db.init_app(app)
login = LoginManager(app)
login.login_view = 'login'
app.app_context().push()

if __name__ == '__main__':
    from routes import * # import put here in order to avoid circular imports
    app.run()
