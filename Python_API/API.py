from main import *

@login_manager.user_loader
async def load_user(user_id):
	return Users.query.get(int(user_id))

async def send_async_email(msg):
	with app.app_context():
		mail.send(msg)

@app.route("/register", methods=["GET", "POST"])
async def register():
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
				return jsonify(message="Incorrect password!")
		else:
			return jsonify(message="Account does not exist!")
	return jsonify(errors=form.errors)

@app.route("/logout", methods=["GET", "POST"])
@login_required
async def logout():
	logout_user()
	return jsonify(message=f"Sign out successful!")

@app.route("/user/<id_user>")
async def user(id_user):
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
async def user_setting(id_user):
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
async def user_setting_password():
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
			return jsonify(message="Please check your email or spam", account={"email": account.email})
		else:
			return jsonify(message="Account does not exist")

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

async def update_participation_time(id_user, participation_time):
	profile = Profiles.query.filter_by(id_user=id_user).first()
	profile.participation_time = participation_time
	db.session.commit()

@app.route('/get_full_img_chapter', methods=['GET', 'POST'])
async def get_full_img_chapter():
    link_chapter = request.form.get("link-chapter")
    chapters = ListChapter.query.filter_by(id_chapter=link_chapter).first()
    list_link_img = chapters.list_image_chapter_server_goc.split(',')
    dict_link_img = dict()
    dict_link_img['list_img'] = list_link_img
    return dict_link_img
	
@app.route("/")
async def get_home():
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
		
	data_news = []
	news = Anime_Manga_News.query.order_by(func.STR_TO_DATE(Anime_Manga_News.time_news, "%b %d, %h:%i %p").desc()).limit(50).all()
	for new in news:
		data = {
			"idNews": new.idNews,
			"time_news": new.time_news,
			"category": new.category,
			"title_news": new.title_news,
			"profile_user_post": new.profile_user_post,
			"images_poster": new.images_poster,
			"descript_pro": new.descript_pro,
			"number_comment": new.number_comment
		}
		data_news.append(data)

	#REVIEWS MANGA
	data_reviews_manga = []
	reviews_manga = Reviews_Manga.query.order_by(func.STR_TO_DATE(Reviews_Manga.time_review, "%b %d, %Y").desc()).limit(50).all()
	for review in reviews_manga:
		data = {
			"idReview": review.idReview,
			"noi_dung": review.noi_dung,
			"link_manga": review.link_manga,
			"link_avatar_user_comment": review.link_avatar_user_comment,
			"link_user": review.link_user,
			"time_review": review.time_review
		}
		data_reviews_manga.append(data)

	# REVIEWS ANIME
	data_reviews_anime = []
	reviews_manga = Reviews_Anime.query.order_by(func.STR_TO_DATE(Reviews_Anime.time_review, "%b %d, %Y").desc()).limit(50).all()
	for review in reviews_manga:
		data = {
			"idReview": review.idReview,
			"noi_dung": review.noi_dung,
			"link_anime": review.link_anime,
			"link_avatar_user_comment": review.link_avatar_user_comment,
			"link_user": review.link_user,
			"time_review": review.time_review
		}
		data_reviews_anime.append(data)

	#RANK WEEK
	data_rank_manga_week = []
	rank_manga_week = ListManga.query.order_by(cast(ListManga.so_luong_view, Integer).desc()).limit(50).all()
	for rank in rank_manga_week:
		data = {
			"id_manga": rank.id_manga,
			"title_manga": rank.title_manga,
			"image_poster_link_goc": rank.link_image_poster_link_goc,
			"so_luong_view": rank.so_luong_view,
			"list_categories": rank.list_categories,
			"author": rank.tac_gia
		}
		data_rank_manga_week.append(data)

	#RANK MONTH
	data_rank_manga_month = []
	rank_manga_month = ListManga.query.order_by(cast(ListManga.so_luong_view, Integer).desc()).limit(50).all()
	for rank in rank_manga_month:
		data = {
			"id_manga": rank.id_manga,
			"title_manga": rank.title_manga,
			"image_poster_link_goc": rank.link_image_poster_link_goc,
			"so_luong_view": rank.so_luong_view,
			"list_categories": rank.list_categories,
			"author": rank.tac_gia
		}
		data_rank_manga_month.append(data)

	#RANK YEAR
	data_rank_manga_year = []
	rank_manga_year = ListManga.query.order_by(cast(ListManga.so_luong_view, Integer).desc()).limit(50).all() # Views is digits
	for rank in rank_manga_year:
		data = {
			"id_manga": rank.id_manga,
			"title_manga": rank.title_manga,
			"image_poster_link_goc": rank.link_image_poster_link_goc,
			"so_luong_view": rank.so_luong_view,
			"list_categories": rank.list_categories,
			"author": rank.tac_gia
		}
		data_rank_manga_year.append(data)

	#COMEDY COMMICS
	data_comedy_comics = []
	comedy_comics = ListManga.query.filter(ListManga.list_categories.like('%Comedy%'))\
		.order_by(func.STR_TO_DATE(ListManga.time_release, "%H:%i:%s %d/%c/%Y").desc()).limit(50).all()
	for comedy_comic in comedy_comics:
		chapter_new = ListChapter.query.filter_by(id_manga=comedy_comic.id_manga).order_by(func.STR_TO_DATE(ListChapter.thoi_gian_release, "%B %d, %Y").desc()).first()
		data = {
			"id_manga": comedy_comic.id_manga,
			"title_manga": comedy_comic.title_manga,
			"image_poster_link_goc": comedy_comic.link_image_poster_link_goc,
			"so_luong_view": comedy_comic.so_luong_view,
			"list_categories": comedy_comic.list_categories,
			"rate": comedy_comic.rate,
			"author": comedy_comic.tac_gia,
			"chapter_new": chapter_new.chapter,
			"id_chapter": chapter_new.id_chapter,
			"time_release": comedy_comic.time_release,
		}
		data_comedy_comics.append(data)

	#FREE COMICS
	data_free_comics = []
	free_comics = ListManga.query.order_by(cast(ListManga.so_luong_view, Integer).desc()).limit(50).all()
	for free_comic in free_comics:
		chapter_new = ListChapter.query.filter_by(id_manga=free_comic.id_manga).order_by(func.STR_TO_DATE(ListChapter.thoi_gian_release, "%B %d, %Y").desc()).first()
		data = {
			"id_manga": free_comic.id_manga,
			"title_manga": free_comic.title_manga,
			"image_poster_link_goc": free_comic.link_image_poster_link_goc,
			"so_luong_view": free_comic.so_luong_view,
			"list_categories": free_comic.list_categories,
			"rate": free_comic.rate,
			"author": free_comic.tac_gia,
			"chapter_new": chapter_new.chapter,
			"id_chapter": chapter_new.id_chapter,
			"time_release": free_comic.time_release,
		}
		data_free_comics.append(data)

	#COOMING SOON COMICS
	data_cooming_soon_comics = []
	cooming_soon_comics = ListManga.query.order_by(cast(ListManga.so_luong_view, Integer).desc()).limit(50).all()
	for cooming_soon_comic in cooming_soon_comics:
		data = {
			"id_manga": cooming_soon_comic.id_manga,
			"title_manga": cooming_soon_comic.title_manga,
			"image_poster": cooming_soon_comic.link_image_poster_link_goc,
			"list_categories": cooming_soon_comic.list_categories,
			"author": cooming_soon_comic.tac_gia,
			"release_date": cooming_soon_comic.time_release,
		}
		data_cooming_soon_comics.append(data)

	#RECOMMENDED COMICS
	data_recommended_comics = []
	recommended_comics = ListManga.query.order_by(cast(ListManga.so_luong_view, Integer).desc()).limit(50).all()
	for recommended_comic in recommended_comics:
		chapter_new = ListChapter.query.filter_by(id_manga=recommended_comic.id_manga)\
			.order_by(func.STR_TO_DATE(ListChapter.thoi_gian_release, "%B %d, %Y").desc()).first()
		data = {
			"id_manga": recommended_comic.id_manga,
			"title_manga": recommended_comic.title_manga,
			"image_poster_link_goc": recommended_comic.link_image_poster_link_goc,
			"so_luong_view": recommended_comic.so_luong_view,
			"list_categories": recommended_comic.list_categories,
			"rate": recommended_comic.rate,
			"author": recommended_comic.tac_gia,
			"chapter_new": chapter_new.chapter,
			"id_chapter": chapter_new.id_chapter,
			"time_release": recommended_comic.time_release,
		}
		data_recommended_comics.append(data)

	#RECENT COMICS
	data_recent_comics = []
	recent_comics = ListManga.query.order_by(cast(ListManga.so_luong_view, Integer).desc()).limit(50).all()
	for recent_comic in recent_comics:
		chapter_new = ListChapter.query.filter_by(id_manga=recent_comic.id_manga)\
			.order_by(func.STR_TO_DATE(ListChapter.thoi_gian_release, "%B %d, %Y").desc()).first()
		data = {
			"id_manga": recent_comic.id_manga,
			"title_manga": recent_comic.title_manga,
			"image_poster_link_goc": recent_comic.link_image_poster_link_goc,
			"so_luong_view": recent_comic.so_luong_view,
			"list_categories": recent_comic.list_categories,
			"rate": recent_comic.rate,
			"author": recent_comic.tac_gia,
			"chapter_new": chapter_new.chapter,
			"id_chapter": chapter_new.id_chapter,
			"time_release": recent_comic.time_release,
		}
		data_recent_comics.append(data)

	#NEW RELEASE COMICS
	data_new_release_comics = []
	new_release_comics = ListManga.query.order_by(cast(ListManga.so_luong_view, Integer).desc()).limit(50).all()
	for new_release_comic in new_release_comics:
		chapter_new = ListChapter.query.filter_by(id_manga=new_release_comic.id_manga)\
			.order_by(func.STR_TO_DATE(ListChapter.thoi_gian_release, "%B %d, %Y").desc()).first()
		data = {
			"id_manga": new_release_comic.id_manga,
			"title_manga": new_release_comic.title_manga,
			"image_poster_link_goc": new_release_comic.link_image_poster_link_goc,
			"so_luong_view": new_release_comic.so_luong_view,
			"list_categories": new_release_comic.list_categories,
			"rate": new_release_comic.rate,
			"author": new_release_comic.tac_gia,
			"chapter_new": chapter_new.chapter,
			"id_chapter": chapter_new.id_chapter,
			"time_release": new_release_comic.time_release,
		}
		data_new_release_comics.append(data)


	return jsonify(User_New=data_user, Anime_Manga_News=data_news, Reviews_Manga=data_reviews_manga, Reviews_Anime=data_reviews_anime,
				   Rank_Manga_Week=data_rank_manga_week, Rank_Manga_Month=data_rank_manga_month, Rank_Manga_Year=data_rank_manga_year,
				   Comedy_Comics=data_comedy_comics, Free_Comics=data_free_comics, Cooming_Soon_Comics=data_cooming_soon_comics,
				   Recommended_Comics=data_recommended_comics, Recent_Comics=data_recent_comics, New_Release_Comics=data_new_release_comics)

