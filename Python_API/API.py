from main import *
from main.home import user_new, anime_manga_news, reviews_manga, reviews_anime, rank_manga_week, rank_manga_month, rank_manga_year
from main.home import comedy_comics, free_comics, cooming_soon_comics, recommended_comics, recent_comics, new_release_comics

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))

def send_async_email(msg):
	with app.app_context():
		mail.send(msg)

@app.route("/register", methods=["GET", "POST"])
async def register():
	form = RegisterForm()
	if request.method == "POST":
		if form.validate_on_submit():
			account = Users.query.filter_by(email=form.email.data).first()
			if account:
				return jsonify(message="Account already exists!"), 400
			else:
				data = {"email": form.email.data, "password": form.password.data}
				token = secret.dumps(data, salt=app.config["SECURITY_PASSWORD_SALT"])
				confirm_url = url_for("register_confirm", token=token, _external=True)
				msg = Message("Confirmation", sender=app.config["MAIL_USERNAME"], recipients=[form.email.data])
				msg.body = "Your confirmation link is " + confirm_url
				thr = Thread(target=send_async_email, args=[msg])
				thr.start()
				return jsonify(message="Please check your email or spam", account={"email": form.email.data}), 200
	return jsonify(errors=form.errors)


@app.route("/register/confirm/<token>")
async def register_confirm(token):
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
async def login():
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
				return jsonify(message="Incorrect password!"), 400
		else:
			return jsonify(message="Account does not exist!"), 404
	return jsonify(errors=form.errors)

@app.route("/logout", methods=["GET", "POST"])
@login_required
async def logout():
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
		return jsonify(message="User does not exist"), 404

@app.route("/user/setting", methods=["PATCH"])
@login_required
async def user_setting():
	form = UserSettingForm()
	id_user = current_user.id_user
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
async def user_setting_password():
	form = SettingPasswordForm()
	if form.validate_on_submit():
		current_password = form.current_password.data
		new_password = form.new_password.data
		confirm_password = form.confirm_password.data

		id_user = current_user.id_user
		account = Users.query.get_or_404(id_user)

		is_password_correct = check_password_hash(account.password, current_password)
		if not is_password_correct:
			return jsonify(message="Incorrect current password"), 400
		else:
			data = {"current_password": current_password, "new_password": new_password,
							"confirm_password": confirm_password, "id_user": account.id_user}
			token = secret.dumps(data, salt=app.config["SECURITY_PASSWORD_SALT"])
			msg = Message("Confirmation", sender=app.config["MAIL_USERNAME"], recipients=[account.email])
			confirm_url = url_for("setting_password_confirm", token=token, _external=True)
			msg.body = "Your confirmation link is " + confirm_url
			thr = Thread(target=send_async_email, args=[msg])
			thr.start()
			return jsonify(message="Please check your email or spam", account={"email": account.email}), 200
	return jsonify(errors=form.errors), 400

@app.route("/setting/password/confirm/<token>")
async def setting_password_confirm(token):
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
async def forgot_password():
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
			return jsonify(message="Please check your email or spam", account={"email": account.email}), 200
		else:
			return jsonify(message="Account does not exist"), 404
	return jsonify(error=form.errors), 400

@app.route("/forgot-password/confirm/<token>")
async def forgot_password_confirm(token):
	try:
		confirmed_email = secret.loads(token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=600)
	except Exception:
		return {"message": "Your link was expired. Try again"}
	hashed_password = generate_password_hash(confirmed_email["new_password"])
	account = Users.query.filter_by(id_user=confirmed_email["id_user"])
	account.password = hashed_password
	db.session.commit()
	return {"message": "Confirm successfully. Try to login"}

@app.route("/")
async def get_home():
	data_news, data_reviews_manga, data_reviews_anime, data_rank_manga_week, data_rank_manga_month, data_rank_manga_year, \
	data_comedy_comics, data_free_comics, data_cooming_soon_comics, data_recommended_comics, \
	data_recent_comics, data_new_release_comics, data_user = await asyncio.gather(
		anime_manga_news(), reviews_manga(), reviews_anime(), rank_manga_week(), rank_manga_month(), rank_manga_year(),
		comedy_comics(), free_comics(), cooming_soon_comics(), recommended_comics(),
		recent_comics(), new_release_comics(), user_new()
	)

	result = [
		{"id": 1, "type": 1, "name": "Recommended Comics", "data": data_recommended_comics},
		{"id": 2, "type": 1, "name": "New Release Comics", "data": data_new_release_comics},
		{"id": 3, "type": 1, "name": "Free Comics", "data": data_free_comics},
		{"id": 4, "type": 1, "name": "Cooming Soon Comics", "data": data_cooming_soon_comics},
		{"id": 5, "type": 1, "name": "Recent Comics", "data": data_recent_comics},
		{"id": 6, "type": 1, "name": "Comedy Comics", "data": data_comedy_comics},

		{"id": 7, "type": 2, "name": "Anime Manga News", "data": data_news},
		{"id": 8, "type": 2, "name": "Reviews Manga", "data": data_reviews_manga},
		{"id": 9, "type": 2, "name": "Reviews Anime", "data": data_reviews_anime},

		{"id": 10, "type": 3, "name": "Rank Week", "data": data_rank_manga_week},
		{"id": 11, "type": 3, "name": "Rank Month", "data": data_rank_manga_month},
		{"id": 12, "type": 3, "name": "Rank Year", "data": data_rank_manga_year},

		{"id": 13, "type": 4, "name": "User New", "data": data_user}
	]
	return jsonify(result)


@app.route('/manga/<path:path_segment_manga>/')
async def get_manga(path_segment_manga):
	manga = List_Manga.query.filter_by(path_segment_manga=path_segment_manga).first()

	if manga == None:
		return jsonify(msg="Manga doesn't exist!"), 404

	localhost = await split_join(request.url)
	chapters = await list_chapter(localhost, manga.id_manga, path_segment_manga)

	return jsonify(
		IdManga=manga.id_manga,
		TitleManga=manga.title_manga,
		DescriptManga=manga.descript_manga,
		Poster=manga.poster_original,
		Categories=manga.categories,
		Rate=manga.rate,
		Views=manga.views_original,
		Status=manga.status,
		Author=manga.author,
		Chapters=chapters
	)

@app.route('/manga/<path_segment_manga>/<path_segment_chapter>/')
async def get_image_chapter(path_segment_manga, path_segment_chapter):
	path_segment = f"{path_segment_manga}-{path_segment_chapter}"
	chapters = Imaga_Chapter.query.filter_by(path_segment=path_segment).first()

	if chapters == None:
		return jsonify(msg="None"), 404

	image_chapter = chapters.image_chapter_original.split(',')
	chapter = List_Chapter.query.filter_by(id_chapter=chapters.id_chapter).first()
	manga = Manga_Update.query.filter_by(id_manga=chapter.id_manga).first()

	manga.views_week += 1
	manga.views_month += 1
	manga.views += 1
	db.session.commit()
	return jsonify(ImageChapter=image_chapter)

