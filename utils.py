from functools import wraps
from models import Role
from extensions import db
from flask_login import current_user

def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            for role in current_user.get_roles():
                if role in roles:
                    return f(*args, **kwargs)
            return error_response()
        return wrapped
    return wrapper
