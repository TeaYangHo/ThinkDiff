# from .model import db, Users, Profiles, Anime_Manga_News, Reviews_Manga, Reviews_Anime, List_Manga, List_Chapter, Manga_Update
from . import *


async def update_participation_time(id_user, participation_time):
	profile = Profiles.query.filter_by(id_user=id_user).first()
	profile.participation_time = participation_time
	db.session.commit()

async def user_new():
	users = Users.query.order_by(func.STR_TO_DATE(Users.time_register, "%H:%i:%S %d-%m-%Y").desc()).limit(20).all()
	for user in users:
		id_user = user.id_user
		time_reg = user.time_register
		participation_time = convert_time(time_reg)
		await update_participation_time(id_user, participation_time)

	users_new = Profiles.query.join(Users, Profiles.id_user == Users.id_user)\
		.order_by(func.STR_TO_DATE(Users.time_register, "%H:%i:%S %d-%m-%Y").desc()).limit(20).all()

	data_user = []
	for user_new in users_new:
		data = {
			"id_user": user_new.id_user,
			"name_user": user_new.name_user,
			"avatar_user": user_new.avatar_user,
			"participation_time": user_new.participation_time
		}
		data_user.append(data)
	return data_user

async def anime_manga_news():
	data_news = []
	news = Anime_Manga_News.query\
		.order_by(func.STR_TO_DATE(Anime_Manga_News.time_news, "%b %d, %h:%i %p").desc()).limit(20).all()
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
	return data_news

#REVIEWS MANGA
async def reviews_manga():
	data_reviews_manga = []
	reviews_manga = Reviews_Manga.query\
		.order_by(func.STR_TO_DATE(Reviews_Manga.time_review, "%b %d, %Y").desc()).limit(20).all()

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
	return data_reviews_manga

# REVIEWS ANIME
async def reviews_anime():
	data_reviews_anime = []
	reviews_manga = Reviews_Anime.query.\
		order_by(func.STR_TO_DATE(Reviews_Anime.time_review, "%b %d, %Y").desc()).limit(20).all()
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
	return data_reviews_anime

#RANK WEEK
async def rank_manga_week():
	data_rank_manga_week = []
	rank_manga_week = Manga_Update.query.order_by(Manga_Update.views_week.desc()).limit(20).all()
	for rank in rank_manga_week:
		localhost = await split_join(request.url)
		data = {
			"id_manga": rank.id_manga,
			"url_manga": await make_link(localhost, rank.path_segment_manga),
			"title_manga": rank.title_manga,
			"image_poster": rank.poster,
			"categories": rank.categories,
			"views_week": rank.views_week
		}
		data_rank_manga_week.append(data)
	return data_rank_manga_week

#RANK MONTH
async def rank_manga_month():
	data_rank_manga_month = []
	rank_manga_month = Manga_Update.query.order_by(Manga_Update.views_month.desc()).limit(20).all()
	for rank in rank_manga_month:
		localhost = await split_join(request.url)
		data = {
			"id_manga": rank.id_manga,
			"url_manga": await make_link(localhost, rank.path_segment_manga),
			"title_manga": rank.title_manga,
			"image_poster": rank.poster,
			"categories": rank.categories,
			"views_month": rank.views_month
		}
		data_rank_manga_month.append(data)
	return data_rank_manga_month

#RANK YEAR
async def rank_manga_year():
	data_rank_manga_year = []
	rank_manga_year = Manga_Update.query.order_by(Manga_Update.views.desc()).limit(20).all()
	for rank in rank_manga_year:
		localhost = await split_join(request.url)
		data = {
			"id_manga": rank.id_manga,
			"url_manga": await make_link(localhost, rank.path_segment_manga),
			"title_manga": rank.title_manga,
			"image_poster": rank.poster,
			"categories": rank.categories,
			"views": rank.views
		}
		data_rank_manga_year.append(data)
	return data_rank_manga_year

#COMEDY COMMICS
async def comedy_comics():
	data_comedy_comics = []
	comedy_comics = Manga_Update.query.filter(Manga_Update.categories.like('%Comedy%')).\
		order_by(func.STR_TO_DATE(Manga_Update.time_release, "%b %d, %Y").desc()).limit(20).all()
	for comedy_comic in comedy_comics:
		localhost = await split_join(request.url)
		data = {
			"id_manga": comedy_comic.id_manga,
			"url_manga": await make_link(localhost, comedy_comic.path_segment_manga),
			"title_manga": comedy_comic.title_manga,
			"image_poster": comedy_comic.poster,
			"rate": comedy_comic.rate,
			"chapter_new": comedy_comic.title_chapter,
			"id_chapter": comedy_comic.id_chapter,
			"url_chapter": await make_link(localhost,
										   f"{comedy_comic.path_segment_manga}/{comedy_comic.path_segment_chapter}"),
			"time_release": comedy_comic.time_release
		}
		data_comedy_comics.append(data)
	return data_comedy_comics

#FREE COMICS
async def free_comics():
	data_free_comics = []
	free_comics = Manga_Update.query.\
		order_by(func.STR_TO_DATE(Manga_Update.time_release, "%b %d, %Y").desc()).limit(20).all()
	for free_comic in free_comics:
		localhost = await split_join(request.url)
		data = {
			"id_manga": free_comic.id_manga,
			"url_manga": await make_link(localhost, free_comic.path_segment_manga),
			"title_manga": free_comic.title_manga,
			"image_poster_link_goc": free_comic.poster,
			"rate": free_comic.rate,
			"chapter_new": free_comic.title_chapter,
			"id_chapter": free_comic.id_chapter,
			"url_chapter": await make_link(localhost,
										f"{free_comic.path_segment_manga}/{free_comic.path_segment_chapter}"),
			"time_release": free_comic.time_release
		}
		data_free_comics.append(data)
	return data_free_comics

#COOMING SOON COMICS
async def cooming_soon_comics():
	data_cooming_soon_comics = []
	cooming_soon_comics = Manga_Update.query.\
		order_by(func.STR_TO_DATE(Manga_Update.time_release, "%b %d, %Y").desc()).limit(20).all()
	for cooming_soon_comic in cooming_soon_comics:
		localhost = await split_join(request.url)
		data = {
			"id_manga": cooming_soon_comic.id_manga,
			"url_manga": await make_link(localhost, cooming_soon_comic.path_segment_manga),
			"title_manga": cooming_soon_comic.title_manga,
			"image_poster_link_goc": cooming_soon_comic.poster,
			"rate": cooming_soon_comic.rate,
			"chapter_new": cooming_soon_comic.title_chapter,
			"id_chapter": cooming_soon_comic.id_chapter,
			"url_chapter": await make_link(localhost,
										f"{cooming_soon_comic.path_segment_manga}/{cooming_soon_comic.path_segment_chapter}"),
			"time_release": cooming_soon_comic.time_release
		}
		data_cooming_soon_comics.append(data)
	return data_cooming_soon_comics

#RECOMMENDED COMICS
async def recommended_comics():
	data_recommended_comics = []
	recommended_comics = Manga_Update.query.\
		order_by(func.STR_TO_DATE(Manga_Update.time_release, "%b %d, %Y").desc()).limit(20).all()
	for recommended_comic in recommended_comics:
		localhost = await split_join(request.url)
		data = {
			"id_manga": recommended_comic.id_manga,
			"url_manga": await make_link(localhost, recommended_comic.path_segment_manga),
			"title_manga": recommended_comic.title_manga,
			"image_poster_link_goc": recommended_comic.poster,
			"rate": recommended_comic.rate,
			"chapter_new": recommended_comic.title_chapter,
			"id_chapter": recommended_comic.id_chapter,
			"url_chapter": await make_link(localhost,
										f"{recommended_comic.path_segment_manga}/{recommended_comic.path_segment_chapter}"),
			"time_release": recommended_comic.time_release
		}
		data_recommended_comics.append(data)
	return data_recommended_comics

#RECENT COMICS
async def recent_comics():
	data_recent_comics = []
	recent_comics = Manga_Update.query.\
		order_by(func.STR_TO_DATE(Manga_Update.time_release, "%b %d, %Y").desc()).limit(20).all()
	for recent_comic in recent_comics:
		localhost = await split_join(request.url)
		data = {
			"id_manga": recent_comic.id_manga,
			"url_manga": await make_link(localhost, recent_comic.path_segment_manga),
			"title_manga": recent_comic.title_manga,
			"image_poster_link_goc": recent_comic.poster,
			"rate": recent_comic.rate,
			"chapter_new": recent_comic.title_chapter,
			"id_chapter": recent_comic.id_chapter,
			"url_chapter": await make_link(localhost,
										f"{recent_comic.path_segment_manga}/{recent_comic.path_segment_chapter}"),
			"time_release": recent_comic.time_release
		}
		data_recent_comics.append(data)

	return data_recent_comics

#NEW RELEASE COMICS
async def new_release_comics():
	data_new_release_comics = []
	new_release_comics = Manga_Update.query.\
		order_by(func.STR_TO_DATE(Manga_Update.time_release, "%b %d, %Y").desc()).limit(20).all()
	for new_release_comic in new_release_comics:
		localhost = await split_join(request.url)
		data = {
			"id_manga": new_release_comic.id_manga,
			"url_manga": await make_link(localhost, new_release_comic.path_segment_manga),
			"title_manga": new_release_comic.title_manga,
			"image_poster_link_goc": new_release_comic.poster,
			"rate": new_release_comic.rate,
			"chapter_new": new_release_comic.title_chapter,
			"id_chapter": new_release_comic.id_chapter,
			"url_chapter": await make_link(localhost,
										f"{new_release_comic.path_segment_manga}/{new_release_comic.path_segment_chapter}"),
			"time_release": new_release_comic.time_release
		}
		data_new_release_comics.append(data)

	return data_new_release_comics
