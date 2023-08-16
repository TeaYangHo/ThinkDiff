from .model import db, Users, Profiles, Anime_Manga_News, Reviews_Manga, Reviews_Anime, List_Manga, List_Chapter, Manga_Update
from .model import Imaga_Chapter, Comments, CommentDiary, LikesComment

from .form import RegisterForm, LoginForm, UserSettingForm, SettingPasswordForm, ForgotPasswordForm, CommentsForm

from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, get_jwt_identity, jwt_required
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
import uuid, os, asyncio
import imgbbpy

app = Flask(__name__)
CORS(app)
app.secret_key = "2458001357900"
app.config["SECURITY_PASSWORD_SALT"] = "2458001357900"
app.config["JWT_SECRET_KEY"] = "2458001357900"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:mcso%40123#%40!@localhost/MANGASOCIAL"
app.config["SQLALCHEMY_BINDS"] = {
    "MYANIMELIST": "mysql://root:mcso%40123#%40!@localhost/MYANIMELIST",
	"MANGASYSTEM": "mysql://root:mcso%40123#%40!@localhost/MANGASYSTEM"
}

app.config["SQLAlCHEMY_TRACK_MODIFICATIONS"] = False

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = "dev.mangasocial@gmail.com"
app.config["MAIL_PASSWORD"] = "deeiumkaqvsxiqwq"
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True

UPLOAD_FOLDER = r"/root/son/mangareader/python_api/"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.config["WTF_CSRF_ENABLED"] = False  # Vô hiệu hóa CSRF

secret = URLSafeTimedSerializer(app.config["SECRET_KEY"])
jwt = JWTManager(app)
mail = Mail(app)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

path_folder_images = "/root/son/mangareader/python_api/"
key_api_imgbb = f'687aae62e4c9739e646a37fca814c1bc'

def convert_time(time):
	time_now = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
	register_date = datetime.strptime(time, "%H:%M:%S %d-%m-%Y")
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

def send_async_email(msg):
	with app.app_context():
		mail.send(msg)

async def list_chapter(localhost, id_manga, path_segment_manga):
	querys = List_Chapter.query.filter_by(id_manga=id_manga).all()

	if querys == None:
		return jsonify(msg="None"), 404

	chapters = []
	for query in querys:
		path_segment_chapter = query.path_segment_chapter
		path = f"{localhost}/manga/{path_segment_manga}/{path_segment_chapter}"
		chapters.append(path)
	return chapters

async def get_comments(path_segment_manga):
	def get_comment_data(comment):
		like_count = LikesComment.query.filter_by(id_comment=comment.id_comment, status="like").count()
		return {
			"id_comment": comment.id_comment,
			"user_id": comment.id_user,
			"content": comment.content,
			"chapter": comment.path_segment_chapter,
			"time_comment": convert_time(comment.time_comment),
			"likes": like_count,
			"is_comment_reply": comment.is_comment_reply,
			"is_edited_comment": comment.is_edited_comment,
			"replies": get_replies(comment.id_comment)
		}

	def get_replies(parent_comment_id):
		replies = (Comments.query.filter_by(reply_id_comment=parent_comment_id)
				   .order_by(func.STR_TO_DATE(Comments.time_comment, "%H:%i:%S %d-%m-%Y").desc()).all())

		reply_data = []
		for reply in replies:
			reply_data.append(get_comment_data(reply))
		return reply_data

	comments = (Comments.query.filter_by(path_segment_manga=path_segment_manga)
				.order_by(func.STR_TO_DATE(Comments.time_comment, "%H:%i:%S %d-%m-%Y").desc()).all())

	comments_info = []
	for comment in comments:
		if comment.is_comment_reply == False:
			comments_info.append(get_comment_data(comment))

	return comments_info

async def delete_reply_comment(comment):
	reply_comments = Comments.query.filter_by(reply_id_comment=comment.id_comment).all()
	for reply_comment in reply_comments:
		await delete_reply_comment(reply_comment)

		comment_diary = CommentDiary(id_comment=reply_comment.id_comment, content=reply_comment.content,
									 comment_type="delete", time_comment=reply_comment.time_comment)
		db.session.add(comment_diary)
		db.session.delete(reply_comment)
		db.session.commit()

async def split_join(url):
	url = url.split('/')
	url = '/'.join(url[:3])
	return url

async def make_link(localhost, path):
	url = f"{localhost}/manga/{path}"
	return url
