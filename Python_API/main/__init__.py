from .model import db, Users, Profiles, Anime_Manga_News, Reviews_Manga, Reviews_Anime, ListManga, ListChapter
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from .form import RegisterForm, LoginForm, UserSettingForm, SettingPasswordForm, ForgotPasswordForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, request, jsonify, url_for
from itsdangerous import URLSafeTimedSerializer
from werkzeug.utils import secure_filename
from sqlalchemy import func, cast, Integer
from datetime import datetime, timedelta
from flask_cors import CORS
from flask_mail import *
from threading import Thread
import uuid, os


app = Flask(__name__)
CORS(app)
app.secret_key = "2458001357900"
app.config["SECURITY_PASSWORD_SALT"] = "2458001357900"
app.config["JWT_SECRET_KEY"] = "2458001357900"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:mcso@123#@!@localhost/MANGASOCIAL"
app.config["SQLALCHEMY_BINDS"] = {
    "MYANIMELIST": "mysql://root:mcso@123#@!@localhost/MYANIMELIST",
	"MANGASYSTEM": "mysql://root:mcso@123#@!@localhost/MANGASYSTEM"
}

app.config["SQLAlCHEMY_TRACK_MODIFICATIONS"] = False

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = "buikhanhtoan_t64@hus.edu.vn"
app.config["MAIL_PASSWORD"] = "mpkehnwnmcziryqs"
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True

UPLOAD_FOLDER = r"images/"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.config["WTF_CSRF_ENABLED"] = False  # Vô hiệu hóa CSRF

secret = URLSafeTimedSerializer(app.config["SECRET_KEY"])
jwt = JWTManager(app)
mail = Mail(app)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

def convert_time(time_register):
	time_now = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
	register_date = datetime.strptime(time_register, "%H:%M:%S %d-%m-%Y")
	current_date = datetime.strptime(time_now, "%H:%M:%S %d-%m-%Y")

	participation_time = current_date - register_date
	if participation_time < timedelta(minutes=1):
		time_in_seconds = participation_time.seconds
		time = f"{time_in_seconds} seconds ago"
	elif participation_time < timedelta(hours=1):
		time_in_minutes = participation_time.seconds // 60
		time = f"{time_in_minutes} minute ago"
	elif participation_time < timedelta(days=1):
		time_in_hours = participation_time.seconds // 3600
		time = f"{time_in_hours} hours ago"
	elif participation_time < timedelta(days=2):
		time = f"Yesterday, " + register_date.strftime("%I:%M %p")
	else:
		time = register_date.strftime("%b %d, %I:%M %p")
	return time

