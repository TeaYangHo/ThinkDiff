from main import *

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(user_id)

@app.route("/register", methods=["GET", "POST"])
def register():
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
				thr = Thread(target=send_email, args=[msg])
				thr.start()
				return jsonify(message="Please check your email or spam", account={"email": form.email.data}), 200
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
				# app.permanent_session_lifetime = timedelta(seconds=10)
				return jsonify(
					message="Login successfully",
					account={"id_user": account.id_user, "email": account.email, "password": account.password}
							)
			else:
				return jsonify(message="Incorrect password!"), 400
		else:
			return jsonify(message="Account does not exist!"), 404
	return jsonify(errors=form.errors), 400


@app.route("/logout")
@login_required
def logout():
	logout_user()
	return jsonify(message=f"Sign out successful!")

@app.route("/user/setting/password", methods=["PATCH", "POST"])
@login_required
def user_setting_password():
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
			thr = Thread(target=send_email, args=[msg])
			thr.start()
			return jsonify(message="Please check your email or spam", account={"email": account.email}), 200
	return jsonify(errors=form.errors), 400

@app.route("/setting/password/confirm/<token>")
def setting_password_confirm(token):
	try:
		confirmed_email = secret.loads(token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=600)
	except Exception:
		return {"message": "Your link was expired. Try again"}
	hashed_password = generate_password_hash(confirmed_email["new_password"])
	account = Users.query.filter_by(id_user=confirmed_email["id_user"]).first()
	account.password = hashed_password
	logout_user()
	db.session.commit()

	return {"message": "Confirm successfully. Try to login"}

@app.route("/forgot-password", methods=["PATCH", "POST"])
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
			thr = Thread(target=send_email, args=[msg])
			thr.start()
			return jsonify(message="Please check your email or spam", account={"email": account.email}), 200
		else:
			return jsonify(message="Account does not exist"), 404
	return jsonify(error=form.errors), 400

@app.route("/forgot-password/confirm/<token>")
def forgot_password_confirm(token):
	try:
		confirmed_email = secret.loads(token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=600)
	except Exception:
		return {"message": "Your link was expired. Try again"}
	hashed_password = generate_password_hash(confirmed_email["new_password"])
	account = Users.query.filter_by(id_user=confirmed_email["id_user"]).first()
	account.password = hashed_password
	db.session.commit()
	return {"message": "Confirm successfully. Try to login"}

@app.route("/user/<id_user>")
def user(id_user):
	account = Users.query.filter_by(id_user=id_user).first()
	profile = Profiles.query.filter_by(id_user=id_user).first()
	if profile and account:
		result = {
			"name_user": profile.name_user,
			"avatar_user": profile.avatar_user,
			"participation_time": convert_time(account.time_register),
			"number_reads": profile.number_reads,
			"number_comments": profile.number_comments,
			"date_of_birth": profile.date_of_birth,
			"gender": profile.gender,
			"introduction": profile.introduction,
			"job": profile.job
		}
		return jsonify(result)
	else:
		return jsonify(message="User does not exist"), 404

@app.route("/user/setting", methods=["PATCH", "POST"])
@login_required
def user_setting():
	form = UserSettingForm()
	id_user = current_user.id_user
	profile_user = Profiles.query.get_or_404(id_user)

	if form.validate_on_submit():
		result = []
		if form.name_user.data:
			profile_user.name_user = form.name_user.data
			data = {"Name User": profile_user.name_user}
			result.append(data)

		if form.date_of_birth.data:
			profile_user.date_of_birth = form.date_of_birth.data.strftime("%d/%m/%Y")
			data = {"Date of birth": profile_user.date_of_birth}
			result.append(data)

		if form.gender.data:
			profile_user.gender = form.gender.data
			data = {"Gender": profile_user.gender}
			result.append(data)

		if form.introduction.data:
			profile_user.introduction = form.introduction.data
			data = {"Introduction": profile_user.introduction}
			result.append(data)

		if form.job.data:
			profile_user.job = form.job.data
			data = {"Job": profile_user.job}
			result.append(data)

		if form.avatar_user.data:
			avatar_file = form.avatar_user.data
			pic_filename = secure_filename(avatar_file.filename)
			formatted = datetime.now().strftime("%H%M%S%f-%d%m%Y")
			pic_name = f"{formatted}-{pic_filename}"
			saver = form.avatar_user.data
			saver.save(os.path.join(app.config["UPLOAD_FOLDER"], pic_name))
			imgbb = f"{path_folder_images}{pic_name}"
			profile_user.avatar_user = imgbb
			data = {"Avatar user": imgbb}
			result.append(data)

		if result:
			db.session.commit()
			return jsonify(message="User Updated Successfully!", data=result)
		else:
			return jsonify(message="No information updated")

	return jsonify(Error=form.errors), 400

