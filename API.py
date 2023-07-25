from main import *

@app.route("/register", methods=["GET", "POST"])
def register():
	if request.method == "POST":
		email = request.form.get("email")
		password = request.form.get("password")

		if email is None and password is None:
			return jsonify(message="Please enter your email and password!")
		elif email is None:
			return jsonify(message="Please enter your email!")
		elif password is None:
			return jsonify(message="Please enter your password!")


		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute("SELECT * FROM USERS WHERE email = %s", [email])
		account = cursor.fetchone()
		cursor.close()
		if account:
			return jsonify(message="Account already exists!")

		elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
			return jsonify(message="Invalid email address!")

		elif not password or not email:
			return jsonify(message="Incorrect email/password!")

		elif len(password) < 8:
			return jsonify(message="Password must be at least 8 characters.")

		else:
			data = {"email": email, "password": password}
			token = secret.dumps(data, salt=app.config["SECURITY_PASSWORD_SALT"])
			msg = Message("Confirmation", sender=app.config["MAIL_USERNAME"], recipients=[email])
			link = url_for("register_confirm", token=token, _external=True)
			msg.body = "Your confirmation link is " + link
			mail.send(msg)
			return jsonify(message="Please check your email or spam", account={"email": email})

@app.route("/register/confirm/<token>")
def register_confirm(token):
	try:
		confirmed_email = secret.loads(token, salt=app.config["SECURITY_PASSWORD_SALT"])
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute("SELECT * FROM USERS WHERE email = %s", (confirmed_email["email"],))
		account = cursor.fetchone()
		if account:
			return jsonify(message="Your account was already confirm")
		else:
			password_hash = generate_password_hash(confirmed_email["password"])
			cursor.execute("INSERT INTO USERS (email, password, time_register) VALUES (%s, %s, %s)",
						   (confirmed_email["email"], password_hash, datetime.now().strftime("%H:%M:%S %d-%m-%Y")))
			mysql.connection.commit()

			cursor.execute("SELECT * FROM USERS WHERE email = %s", (confirmed_email["email"],))
			user = cursor.fetchone()
			insert_profiles_parameter = """INSERT INTO PROFILES
														(id_user, name_user, avatar_user, participation_time)
														VALUES (%s, %s, %s, %s);"""
			insert_profiles_data = (user["id_user"], user["email"], f"Ảnh mặc định", convert_time(user["time_register"]))
			cursor.execute(insert_profiles_parameter, insert_profiles_data)
			cursor.close()
			mysql.connection.commit()
	except Exception:
		return {"message": "Your link was expired. Try again"}

	return {"message": "Confirm successfully. Try to login"}

@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		email = request.form.get("email")
		password = request.form.get("password")
		if email is None and password is None:
			return jsonify(message="Please enter your email and password!")
		elif email is None:
			return jsonify(message="Please enter your email!")
		elif password is None:
			return jsonify(message="Please enter your password!")

		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute("SELECT * FROM USERS WHERE email = %s", (email,))
		account = cursor.fetchone()
		cursor.close()

		if account:
			is_pass_correct = check_password_hash(account["password"], password)
			if is_pass_correct:
				session["id_user"] = account["id_user"]
				session["email"] = account["email"]
				print(session["id_user"])
				access_token = create_access_token(identity={"id_user": account["id_user"], "email": account["email"], "password": account["password"]})
				return jsonify(message="Login successfully",
						account={"id_user": account["id_user"], "email": account["email"], "password": account["password"],
								"jwt": access_token})
			else:
				return jsonify(message="Incorrect password!")
		else:
			return jsonify(message="Account does not exist!")

@app.route("/logout", methods=["POST"])
def logout():
	if not session.get("id_user"):
		return jsonify(message="Không đăng nhập") #return redirect("home")

	if session.get("id_user"):
		session["id_user"] = None
		session["email"] = None
		return jsonify(message=f"Đăng xuất thành công") #return redirect("home")

@app.route("/user/<id_user>")
def user(id_user):
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute("SELECT * FROM PROFILES WHERE id_user = %s", (id_user,))
	profiles = cursor.fetchone()

	if profiles:
		cursor.execute("SELECT * FROM USERS WHERE id_user = %s", (id_user,))
		account = cursor.fetchone()

		time_reg = account["time_register"]
		participation_time = convert_time(time_reg)
		cursor.execute("UPDATE PROFILES SET participation_time = %s WHERE id_user = %s",
					   (participation_time, id_user))
		mysql.connection.commit()

		cursor.execute("SELECT * FROM PROFILES WHERE id_user = %s", (id_user,))
		profiles_user = cursor.fetchone()
		cursor.close()
		return jsonify(PROFILES={
				"name_user": profiles_user["name_user"],
				"avatar_user": profiles_user["avatar_user"],
				"participation_time": profiles_user["participation_time"],
				"number_reads": profiles_user["number_reads"],
				"number_comments": profiles_user["number_comments"],
				"year_birth": profiles_user["year_birth"],
				"sex": profiles_user["sex"],
				"introduction": profiles_user["introduction"]
				})
	else:
		return jsonify(message= "User does not exist")

@app.route("/user/<id_user>/setting", methods=["PATCH"])
def user_setting(id_user):
	if session.get("id_user"):
		if request.method == "PATCH":
			name_user = request.form.get("name_user")
			avatar_user = request.form.get("avatar_user")#FileField("Profile Pic")
			year_birth = request.form.get("year_birth")
			sex = request.form.get("sex")
			introduction = request.form.get("introduction")

			if name_user is None and avatar_user is None and year_birth is None and sex is None and introduction is None:
				return redirect(f"/user/{id_user}")

			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			update_parameters = "UPDATE PROFILES SET"
			update_data = []

			if name_user is not None:
				update_parameters += " name_user=%s,"
				update_data.append(name_user)
			if avatar_user is not None:
				update_parameters += " avatar_user=%s,"
				update_data.append(avatar_user)
			if year_birth is not None:
				update_parameters += " year_birth=%s,"
				update_data.append(year_birth)
			if sex is not None:
				update_parameters += " sex=%s,"
				update_data.append(sex)
			if introduction is not None:
				update_parameters += " introduction=%s,"
				update_data.append(introduction)
			update_parameters = update_parameters.rstrip(",") + " WHERE id_user=%s"
			update_data.append(id_user)

			cursor.execute(update_parameters, tuple(update_data))
			cursor.close()
			mysql.connection.commit()
			return redirect(f"/user/{id_user}")
	else:
		return jsonify(message="Not logged in")

@app.route("/user/setting/password", methods=["PATCH"])
def user_setting_password():
	if session.get("id_user"):
		if request.method == "PATCH":
			current_password = request.form.get("current_password")
			new_password = request.form.get("new_password")
			confirm_password = request.form.get("confirm_password")

			if not current_password or not new_password or not confirm_password:
				return jsonify(message="Missing password parameters")

			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute("SELECT * FROM USERS WHERE id_user = %s", (session["id_user"],))
			account = cursor.fetchone()
			cursor.close()
			if not account:
				return jsonify(message="User not found")

			is_password_correct = check_password_hash(account["password"], current_password)
			if not is_password_correct:
				return jsonify(message="Incorrect current password")

			if len(new_password) < 8:
				return jsonify(message="Password must be at least 8 characters.")

			if new_password != confirm_password:
				return jsonify(message="New password and confirm password do not match")

			else:
				data = {"current_password": current_password, "new_password": new_password,
								"confirm_password": confirm_password, "id_user": account["id_user"]}
				token = secret.dumps(data, salt=app.config["SECURITY_PASSWORD_SALT"])
				msg = Message("Confirmation", sender=app.config["MAIL_USERNAME"], recipients=[account["email"]])
				link = url_for("setting_password_confirm", token=token, _external=True)
				msg.body = "Your confirmation link is " + link
				mail.send(msg)
				return jsonify(message="Please check your email or spam", account={"email": account["email"]})
	else:
		return jsonify(message="Not logged in")

@app.route("/setting/password/confirm/<token>")
def setting_password_confirm(token):
	try:
		confirmed_email = secret.loads(token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=600)
	except Exception:
		return {"message": "Your link was expired. Try again"}

	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	hashed_password = generate_password_hash(confirmed_email["new_password"])
	cursor.execute("UPDATE USERS SET password = %s WHERE id_user = %s", (hashed_password, confirmed_email["id_user"]))
	mysql.connection.commit()
	cursor.close()
	return {"message": "Confirm successfully. Try to login"}

@app.route("/forgot-password", methods=["PATCH"])
def forgot_password():
	if request.method == "PATCH":
		email = request.form.get("email")
		new_password = request.form.get("new_password")
		confirm_password = request.form.get("confirm_password")
		if not email:
			return jsonify(message="Missing email parameters")

		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute("SELECT * FROM USERS WHERE email = %s", (email,))
		account = cursor.fetchone()
		cursor.close()
		if account:
			if not new_password or not confirm_password:
				return jsonify(message="Missing password parameters")
			if len(new_password) < 8:
				return jsonify(message="Password must be at least 8 characters.")
			if new_password != confirm_password:
				return jsonify(message="New password and confirm password do not match")
			else:
				data = {"email": email, "new_password": new_password, "confirm_password": confirm_password, "id_user": account["id_user"]}
				token = secret.dumps(data, salt=app.config["SECURITY_PASSWORD_SALT"])
				msg = Message("Confirmation", sender=app.config["MAIL_USERNAME"], recipients=[account["email"]])
				link = url_for("forgot_password_confirm", token=token, _external=True)
				msg.body = "Your confirmation link is " + link
				mail.send(msg)
				return jsonify(message="Please check your email or spam", account={"email": account["email"]})
		else:
			return jsonify(message="Account does not exist")

@app.route("/forgot-password/confirm/<token>")
def forgot_password_confirm(token):
	try:
		confirmed_email = secret.loads(token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=600)
	except Exception:
		return {"message": "Your link was expired. Try again"}

	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	hashed_password = generate_password_hash(confirmed_email["new_password"])
	cursor.execute("UPDATE USERS SET password = %s WHERE id_user = %s", (hashed_password, confirmed_email["id_user"]))
	mysql.connection.commit()
	cursor.close()
	return {"message": "Confirm successfully. Try to login"}

def get_users(cursor):
	select_query = """SELECT * FROM USERS"""
	cursor.execute(select_query)
	users = cursor.fetchall()
	return users

def update_participation_time(id_user, participation_time, cursor):
	update_query = """UPDATE PROFILES
					SET participation_time = %s
					WHERE id_user = %s"""
	cursor.execute(update_query, (participation_time, id_user))
	mysql.connection.commit()

@app.route("/home")
def anime_manga_news():
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	users = get_users(cursor)
	for user in users:
		id_user = user["id_user"]
		time_reg = user["time_register"]
		participation_time = convert_time(time_reg)
		update_participation_time(id_user, participation_time, cursor)

	User_New_Register = f"""
	SELECT PROFILES.name_user, PROFILES.avatar_user, PROFILES.participation_time
	FROM PROFILES
	JOIN USERS ON PROFILES.id_user = USERS.id_user
	ORDER BY STR_TO_DATE(USERS.time_register, "%H:%i:%S %d-%m-%Y") DESC
	LIMIT {50};
	"""
	cursor.execute(User_New_Register)
	user_new_register = cursor.fetchall()

	cursor.execute("USE MYANIMELIST;")
	Anime_Manga_News = f"""
	SELECT * FROM MYANIMELIST.Anime_Manga_News
	ORDER BY STR_TO_DATE(time_news, "%b %d, %h:%i %p") DESC
	LIMIT {50};
	"""
	Reviews_Anime = f"""
	SELECT * FROM MYANIMELIST.Reviews_Anime
	ORDER BY STR_TO_DATE(time_review, "%b %d, %Y") DESC
	LIMIT {50};
	"""

	Reviews_Manga = f"""
	SELECT * FROM MYANIMELIST.Reviews_Manga
	ORDER BY STR_TO_DATE(time_review, "%b %d, %Y") DESC
	LIMIT {50};
	"""

	cursor.execute(Anime_Manga_News)
	anime_manga_news = cursor.fetchall()

	cursor.execute(Reviews_Anime)
	review_anime = cursor.fetchall()

	cursor.execute(Reviews_Manga)
	review_manga = cursor.fetchall()
	cursor.close()

	return jsonify(Anime_Manga_News=anime_manga_news, Reviews_Anime=review_anime, Reviews_Manga=review_manga, User_New_Register=user_new_register)
