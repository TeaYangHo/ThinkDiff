from main import *
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from form import RegisterForm, LoginForm, UserSettingForm, SettingPasswordForm, ForgotPasswordForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, request, jsonify, redirect, url_for
from itsdangerous import URLSafeTimedSerializer
from werkzeug.utils import secure_filename
from sqlalchemy import func

from flask_cors import CORS
from flask_mail import *
from threading import Thread
import MySQLdb.cursors
import re, uuid, os

from model import Users, Profiles, db

app = Flask(__name__)
CORS(app)
app.secret_key = "2458001357900"
app.config["SECURITY_PASSWORD_SALT"] = "2458001357900"
app.config["JWT_SECRET_KEY"] = "2458001357900"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@localhost/MANGASOCIAL"
app.config["SQLALCHEMY_BINDS"] = {
    "MYANIMELIST": "mysql://root:@localhost/MYANIMELIST",
	"MANGASYSTEM": "mysql://root:@localhost/MANGASYSTEM"
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

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))

def send_async_email(msg):
	with app.app_context():
		mail.send(msg)

@app.route("/register", methods=["GET", "POST"])
def register():
	form = RegisterForm()
	if request.method == "POST":
		if form.validate_on_submit():
			account = Users.query.filter_by(email=form.email.data).first()
			if account:
				return jsonify(message="Account already exists!")
			else:
				data = {"email": form.email.data, "password": form.password.data}
				token = secret.dumps(data, salt=app.config["SECURITY_PASSWORD_SALT"])
				confirm_url = url_for("register_confirm", token=token, _external=True)
				msg = Message("Confirmation", sender=app.config["MAIL_USERNAME"], recipients=[form.email.data])
				msg.body = "Your confirmation link is " + confirm_url
				thr = Thread(target=send_async_email, args=[msg])
				thr.start()
				return jsonify(message="Please check your email or spam", account={"email": form.email.data})
	return jsonify(errors=form.errors)


@app.route("/register/confirm/<token>")
def register_confirm(token):
	try:
		confirmed_email = secret.loads(token, salt=app.config["SECURITY_PASSWORD_SALT"])
	except Exception:
		return {"message": "Your link was expired. Try again"}

	account = Users.query.filter_by(email=confirmed_email["email"]).first()
	if account:
		return jsonify(message="Your account was already confirm")
	else:
		email_user = confirmed_email["email"]
		password_hash = generate_password_hash(confirmed_email["password"])
		time = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
		user = Users(email=email_user, password=password_hash, time_register=time)
		db.session.add(user)
		db.session.commit()
		find_user = Users.query.filter_by(email=confirmed_email["email"]).first()
		profile = Profiles(id_user=find_user.id_user, name_user=find_user.email, participation_time=convert_time(user.time_register))
		db.session.add(profile)
		db.session.commit()
	return {"message": "Confirm successfully. Try to login"}

@app.route("/login", methods=["GET", "POST"])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		account = Users.query.filter_by(email=form.email.data).first()
		if account:
			is_pass_correct = check_password_hash(account.password, form.password.data)
			if is_pass_correct:
				login_user(account)
				access_token = create_access_token(identity={"id_user": account.id_user, "email": account.email, "password": account.password})
				return jsonify(message="Login successfully",
						account={"id_user": account.id_user, "email": account.email, "password": account.password,
								"jwt": access_token})
			else:
				return jsonify(message="Incorrect password!")
		else:
			return jsonify(message="Account does not exist!")
	return jsonify(errors=form.errors)

@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
	logout_user()
	return jsonify(message=f"Sign out successful!")

@app.route("/user/<id_user>")
def user(id_user):
	profile = Profiles.query.filter_by(id_user=id_user).first()
	if profile:
		account = Users.query.filter_by(id_user=id_user).first()
		time_reg = account.time_register

		participation_time = convert_time(time_reg)
		profile = Profiles.query.filter_by(id_user=id_user).first()
		profile.participation_time = participation_time
		db.session.commit()

		profiles = Profiles.query.filter_by(id_user=id_user).first()
		return jsonify(PROFILES={
				"name_user": profiles.name_user,
				"avatar_user": profiles.avatar_user,
				"participation_time": profiles.participation_time,
				"number_reads": profiles.number_reads,
				"number_comments": profiles.number_comments,
				"year_birth": profiles.year_birth,
				"sex": profiles.sex,
				"introduction": profiles.introduction
				})
	else:
		return jsonify(message="User does not exist")

@app.route("/user/<id_user>/setting", methods=["PATCH"])
@login_required
def user_setting(id_user):
	form = UserSettingForm()
	profile_user = Profiles.query.get_or_404(id_user)
	if form.validate_on_submit():
		profile_user.name_user = form.name_user.data
		profile_user.year_birth = form.year_birth.data
		profile_user.sex = form.sex.data
		profile_user.introduction = form.introduction.data

		if form.avatar_user.data:
			avatar_file = form.avatar_user.data
			pic_filename = secure_filename(avatar_file.filename)
			pic_name = str(uuid.uuid1()) + "_" + pic_filename
			saver = form.avatar_user.data
			saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
		db.session.commit()

@app.route("/user/setting/password", methods=["PATCH"])
@login_required
def user_setting_password():
	form = SettingPasswordForm()
	if form.validate_on_submit():
		current_password = form.current_password.data
		new_password = form.new_password.data
		confirm_password = form.confirm_password.data

		account = Users.query.filter_by(id_user=current_user.id_user).first()
		print(account.email)

		is_password_correct = check_password_hash(account.password, current_password)
		if not is_password_correct:
			return jsonify(message="Incorrect current password")
		else:
			data = {"current_password": current_password, "new_password": new_password,
							"confirm_password": confirm_password, "id_user": account.id_user}
			token = secret.dumps(data, salt=app.config["SECURITY_PASSWORD_SALT"])
			msg = Message("Confirmation", sender=app.config["MAIL_USERNAME"], recipients=[account.email])
			confirm_url = url_for("setting_password_confirm", token=token, _external=True)
			msg.body = "Your confirmation link is " + confirm_url
			thr = Thread(target=send_async_email, args=[msg])
			thr.start()
			return jsonify(message="Please check your email or spam", account={"email": account.email})
	return jsonify(errors=form.errors)

@app.route("/setting/password/confirm/<token>")
def setting_password_confirm(token):
	try:
		confirmed_email = secret.loads(token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=600)
	except Exception:
		return {"message": "Your link was expired. Try again"}
	hashed_password = generate_password_hash(confirmed_email["new_password"])
	account = Users.query.filter_by(id_user=confirmed_email["id_user"]).first()
	account.password = hashed_password
	db.session.commit()

	return {"message": "Confirm successfully. Try to login"}

@app.route("/forgot-password", methods=["PATCH"])
def forgot_password():
	form = ForgotPasswordForm()
	if form.validate_on_submit():
		email = form.email.data
		new_password = form.new_password.data
		confirm_password = form.confirm_password.data

		account = Users.query.filter_by(email=email).first()
		if account:
			data = {"email": email, "new_password": new_password, "confirm_password": confirm_password, "id_user": account.id_user}
			token = secret.dumps(data, salt=app.config["SECURITY_PASSWORD_SALT"])
			msg = Message("Confirmation", sender=app.config["MAIL_USERNAME"], recipients=[account.email])
			confirm_url = url_for("forgot_password_confirm", token=token, _external=True)
			msg.body = "Your confirmation link is " + confirm_url
			thr = Thread(target=send_async_email, args=[msg])
			thr.start()
			return jsonify(message="Please check your email or spam", account={"email": account.email})
		else:
			return jsonify(message="Account does not exist")

@app.route("/forgot-password/confirm/<token>")
def forgot_password_confirm(token):
	try:
		confirmed_email = secret.loads(token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=600)
	except Exception:
		return {"message": "Your link was expired. Try again"}
	hashed_password = generate_password_hash(confirmed_email["new_password"])
	account = Users.query.filter_by(id_user=confirmed_email["id_user"])
	account.password = hashed_password
	db.session.commit()
	return {"message": "Confirm successfully. Try to login"}

def update_participation_time(id_user, participation_time):
	profile = Profiles.query.filter_by(id_user=id_user).first()
	profile.participation_time = participation_time
	db.session.commit()

@app.route("/home")
def anime_manga_news():
	users = Users.query.order_by(func.STR_TO_DATE(Users.time_register, "%H:%i:%S %d-%m-%Y").desc()).limit(20).all()
	for user in users:
		id_user = user.id_user
		time_reg = user.time_register
		participation_time = convert_time(time_reg)
		update_participation_time(id_user, participation_time)

	users_new = Profiles.query.join(Users, Profiles.id_user == Users.id_user)\
		.order_by(func.STR_TO_DATE(Users.time_register, "%H:%i:%S %d-%m-%Y").asc()).limit(50).all()

	data_user = []
	for user_new in users_new:
		data = {
			"id_user": user_new.id_user,
			"name_user": user_new.name_user,
			"avatar_user": user_new.avatar_user,
			"participation_time": user_new.participation_time
		}
		data_user.append(data)

	return jsonify(user=data_user)
	# User_New_Register = f"""dt = [user_new.id_user, user_new.name_user, user_new.avatar_user, user_new.participation_time]
	# SELECT PROFILES.id_user, PROFILES.name_user, PROFILES.avatar_user, PROFILES.participation_time
	# FROM PROFILES
	# JOIN USERS ON PROFILES.id_user = USERS.id_user
	# ORDER BY STR_TO_DATE(USERS.time_register, "%H:%i:%S %d-%m-%Y") DESC
	# LIMIT {50};
	# """
	# cursor.execute(User_New_Register)
	# user_new_register = cursor.fetchall()
	#
	# cursor.execute("USE MYANIMELIST;")
	# Anime_Manga_News = f"""
	# SELECT * FROM MYANIMELIST.Anime_Manga_News
	# ORDER BY STR_TO_DATE(time_news, "%b %d, %h:%i %p") DESC
	# LIMIT {50};
	# """
	# Reviews_Anime = f"""
	# SELECT * FROM MYANIMELIST.Reviews_Anime
	# ORDER BY STR_TO_DATE(time_review, "%b %d, %Y") DESC
	# LIMIT {50};
	# """
	#
	# Reviews_Manga = f"""
	# SELECT * FROM MYANIMELIST.Reviews_Manga
	# ORDER BY STR_TO_DATE(time_review, "%b %d, %Y") DESC
	# LIMIT {50};
	# """
	#
	# cursor.execute(Anime_Manga_News)
	# anime_manga_news = cursor.fetchall()
	#
	# cursor.execute(Reviews_Anime)
	# review_anime = cursor.fetchall()
	#
	# cursor.execute(Reviews_Manga)
	# review_manga = cursor.fetchall()
	# cursor.close()
	#
	# return jsonify(Anime_Manga_News=anime_manga_news, Reviews_Anime=review_anime, Reviews_Manga=review_manga, User_New_Register=user_new_register)