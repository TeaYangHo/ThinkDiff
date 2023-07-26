# from flask_login import UserMixin
# from . import db
#
# class Users(db.Model, UserMixin):
# 	__tablename__ = 'USERS'
# 	id_user = db.Column(db.Integer, primary_key=True, autoincrement=True)
# 	email = db.Column(db.String(250), nullable=False, unique=True)
# 	password = db.Column(db.String(250), nullable=False)
# 	time_register = db.Column(db.String(250), nullable=False)
#
#
# class Profiles(db.Model):
# 	__tablename__ = 'PROFILES'
# 	id_user = db.Column(db.Integer, db.ForeignKey('USERS.id_user'), primary_key=True)
# 	name_user = db.Column(db.String(250), unique=True, default=Users.email)
# 	avatar_user = db.Column(db.String(250), default="https://ibb.co/PMqyby4")
# 	participation_time = db.Column(db.String(250))
# 	number_reads = db.Column(db.Integer)
# 	number_comments = db.Column(db.Integer)
# 	year_birth = db.Column(db.Integer)
# 	sex = db.Column(db.String(11))
# 	introduction = db.Column(db.Text)
