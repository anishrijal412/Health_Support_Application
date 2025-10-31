# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from flask_mail import Mail


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()  


# Redirect unauthorized users to login page
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
