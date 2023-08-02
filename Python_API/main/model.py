from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model, UserMixin):
	__tablename__ = 'USERS'
	id_user = db.Column(db.Integer, primary_key=True, autoincrement=True)
	email = db.Column(db.String(250), nullable=False, unique=True)
	password = db.Column(db.String(250), nullable=False)
	time_register = db.Column(db.String(250), nullable=False)

	def get_id(self):
		return self.id_user

class Profiles(db.Model):
	__tablename__ = 'PROFILES'
	id_user = db.Column(db.Integer, db.ForeignKey('USERS.id_user'), primary_key=True)
	name_user = db.Column(db.String(250), unique=True)
	avatar_user = db.Column(db.String(250), default="https://ibb.co/PMqyby4")
	participation_time = db.Column(db.String(250))
	number_reads = db.Column(db.Integer)
	number_comments = db.Column(db.Integer)
	year_birth = db.Column(db.Integer)
	sex = db.Column(db.String(11))
	introduction = db.Column(db.Text)

class Anime_Manga_News(db.Model):
	__tablename__ = "Anime_Manga_News"
	__bind_key__ = "MYANIMELIST"
	idNews = db.Column(db.String(500), primary_key=True)
	time_news = db.Column(db.Text)
	category = db.Column(db.Text)
	title_news = db.Column(db.Text)
	profile_user_post = db.Column(db.Text)
	images_poster = db.Column(db.Text)
	descript_pro = db.Column(db.Text)
	number_comment = db.Column(db.Integer)

class Reviews_Anime(db.Model):
	__tablename__ = "Reviews_Anime"
	__bind_key__ = "MYANIMELIST"
	idReview = db.Column(db.String(500), primary_key=True)
	noi_dung = db.Column(db.Text)
	link_anime = db.Column(db.Text)
	link_avatar_user_comment = db.Column(db.Text)
	link_user = db.Column(db.Text)
	time_review = db.Column(db.Text)

class Reviews_Manga(db.Model):
	__tablename__ = "Reviews_Manga"
	__bind_key__ = "MYANIMELIST"
	idReview = db.Column(db.String(500), primary_key=True)
	noi_dung = db.Column(db.Text)
	link_manga = db.Column(db.Text)
	link_avatar_user_comment = db.Column(db.Text)
	link_user = db.Column(db.Text)
	time_review = db.Column(db.Text)

class List_Manga(db.Model):
	__tablename__ = "List_Manga"
	__bind_key__ = "MANGASYSTEM"
	id_manga_original = db.Column(db.String(500), primary_key=True)
	id_manga_system = db.Column(db.Text)
	title_manga = db.Column(db.Text)
	descript_manga = db.Column(db.Text)
	poster_upload = db.Column(db.Text)
	poster_original = db.Column(db.Text)
	detail_manga = db.Column(db.Text)
	categories = db.Column(db.Text)
	chapters = db.Column(db.Text)
	rate = db.Column(db.Text)
	views_original = db.Column(db.Text)
	status = db.Column(db.Text)
	author = db.Column(db.Text)
	id_server = db.Column(db.Text)

class List_Chapter(db.Model):
	__tablename__ = "List_Chapter"
	__bind_key__ = "MANGASYSTEM"
	id_chapter_original = db.Column(db.String(500), primary_key=True)
	title_chapter = db.Column(db.Text)
	id_manga_original = db.Column(db.String(500), db.ForeignKey('List_Manga.id_manga_original'))
	id_manga_system = db.Column(db.Text)
	image_chapter_upload = db.Column(db.Text)
	image_chapter_original = db.Column(db.Text)
	time_release = db.Column(db.Text)

class Manga_Update(db.Model):
	__tablename__ = "Manga_Update"
	__bind_key__ = "MANGASYSTEM"
	id_manga_original = db.Column(db.String(500), db.ForeignKey('List_Manga.id_manga_original'), primary_key=True)
	id_manga_system = db.Column(db.Text)
	title_manga = db.Column(db.Text)
	poster = db.Column(db.Text)
	categories = db.Column(db.Text)
	rate = db.Column(db.Text)
	views_week = db.Column(db.Integer, default=0)
	views_month = db.Column(db.Integer, default=0)
	views = db.Column(db.Integer, default=0)
	id_chapter_original = db.Column(db.String(500), db.ForeignKey('List_Chapter.id_chapter_original'))
	title_chapter = db.Column(db.Text)
	time_release = db.Column(db.Text)
