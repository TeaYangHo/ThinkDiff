from .model import db, Users, Profiles, Anime_Manga_News, Reviews_Manga, Reviews_Anime, List_Manga, List_Chapter, Manga_Update
from .model import Imaga_Chapter, Comments, CommentDiary, LikesComment, Comment_News
from .form import RegisterForm, LoginForm, UserSettingForm, SettingPasswordForm, ForgotPasswordForm, CommentsForm

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import Flask, request, jsonify, url_for
from flask_caching import Cache
from flask_cors import CORS
from flask_mail import *

from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from itsdangerous import URLSafeTimedSerializer

from sqlalchemy import func, cast, Integer
from datetime import datetime, timedelta

from urllib.parse import unquote
from threading import Thread
import imgbbpy, os

app = Flask(__name__)
CORS(app)

app.config["SECRET_KEY"] = "24580101357900"
app.config["SECURITY_PASSWORD_SALT"] = "24580201357900"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:ThinkDiff102@localhost/MANGASOCIAL"
app.config["SQLALCHEMY_BINDS"] = {
    "MYANIMELIST": "mysql://root:ThinkDiff102@localhost/MYANIMELIST",
	"MANGASYSTEM": "mysql://root:ThinkDiff102@localhost/MANGASYSTEM"
}

app.config["SQLAlCHEMY_TRACK_MODIFICATIONS"] = False
app.config["WTF_CSRF_ENABLED"] = False

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = "dev.mangasocial@gmail.com"
app.config["MAIL_PASSWORD"] = "deeiumkaqvsxiqwq"
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True

UPLOAD_FOLDER = r"/root/son/mangareader/python_api/"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
cache.init_app(app)

secret = URLSafeTimedSerializer(app.config["SECRET_KEY"])
mail = Mail(app)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

path_folder_images = "/root/son/mangareader/python_api/images/"
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

def send_email(msg):
	with app.app_context():
		mail.send(msg)

def list_chapter(localhost, id_manga, path_segment_manga):
	querys = List_Chapter.query.filter_by(id_manga=id_manga).all()

	if querys == None:
		return jsonify(msg="None"), 404

	chapters = []
	for query in querys:
		path_segment_chapter = query.path_segment_chapter
		path = f"{localhost}/manga/{path_segment_manga}/{path_segment_chapter}"
		chapters.append(path)
	return chapters

def get_comments(path_segment_manga):
	def get_comment_data(comment):
		like_count = LikesComment.query.filter_by(id_comment=comment.id_comment, status="like").count()
		profile = Profiles.query.filter_by(id_user=comment.id_user).first()
		return {
			"id_comment": comment.id_comment,
			"id_user": comment.id_user,
			"name_user": profile.name_user,
			"avatar_user": profile.avatar_user,
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

def delete_reply_comment(comment):
	reply_comments = Comments.query.filter_by(reply_id_comment=comment.id_comment).all()
	for reply_comment in reply_comments:
		delete_reply_comment(reply_comment)

		comment_diary = CommentDiary(id_comment=reply_comment.id_comment, content=reply_comment.content,
									 comment_type="delete", time_comment=reply_comment.time_comment)
		db.session.add(comment_diary)
		db.session.delete(reply_comment)
		db.session.commit()

def update_participation_time(id_user, participation_time):
	profile = Profiles.query.filter_by(id_user=id_user).first()
	profile.participation_time = participation_time
	db.session.commit()
def split_join(url):
	url = url.split('/')
	url = '/'.join(url[:3])
	return url

def make_link(localhost, path):
	url = f"{localhost}{path}"
	return url

def conver_url(url):
	if url.endswith(".html"):
		result = url.split("/")[-1].replace(".html", "")
	elif url.endswith("/"):
		result = url.split("/")[-2]
	elif url.endswith("/all-pages"):
		result = url.split("/")[-2]
	else:
		result = url.split("/")[-1]
	result = unquote(result).replace("/", "")
	return result

def upload_image(api_key, images_name, folder_images):
	client = imgbbpy.SyncClient(api_key)

	try:
		image = client.upload(file=f"{folder_images}{images_name}")
		imgbb = image.url
	except Exception as e:
		return {"Error": str(e)}, 400
	finally:
		path_image = f"{folder_images}{images_name}"
		os.remove(path_image)

	return imgbb
