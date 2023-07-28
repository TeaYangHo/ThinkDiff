from .model import db, Users, Profiles, Anime_Manga_News, Reviews_Manga, Reviews_Anime, ListManga, ListChapter
from . import func, convert_time, cast, Integer

# from . import *

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
		.order_by(func.STR_TO_DATE(Users.time_register, "%H:%i:%S %d-%m-%Y").asc()).limit(20).all()

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
	news = Anime_Manga_News.query.order_by(func.STR_TO_DATE(Anime_Manga_News.time_news, "%b %d, %h:%i %p").desc()).limit(20).all()
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
	reviews_manga = Reviews_Manga.query.order_by(func.STR_TO_DATE(Reviews_Manga.time_review, "%b %d, %Y").desc())\
		.limit(20).all()
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
	# REVIEWS ANIME
	data_reviews_anime = []
	reviews_manga = Reviews_Anime.query.order_by(func.STR_TO_DATE(Reviews_Anime.time_review, "%b %d, %Y").desc())\
		.limit(20).all()
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
	rank_manga_week = ListManga.query.order_by(cast(ListManga.so_luong_view, Integer).desc()).limit(20).all()
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
	return data_rank_manga_week

#RANK MONTH
async def rank_manga_month():
	data_rank_manga_month = []
	rank_manga_month = ListManga.query.order_by(cast(ListManga.so_luong_view, Integer).desc()).limit(20).all()
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
	return data_rank_manga_month

#RANK YEAR
async def rank_manga_year():
	data_rank_manga_year = []
	rank_manga_year = ListManga.query.order_by(cast(ListManga.so_luong_view, Integer).desc()).limit(
		20).all()  # Views is digits
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
	return data_rank_manga_year

#COMEDY COMMICS
async def comedy_comics():
	data_comedy_comics = []
	comedy_comics = ListManga.query.filter(ListManga.list_categories.like('%Comedy%')) \
		.order_by(cast(ListManga.so_luong_view, Integer).desc()).limit(20).all()
	for comedy_comic in comedy_comics:
		chapter_new = ListChapter.query.filter_by(id_manga=comedy_comic.id_manga) \
			.order_by(func.STR_TO_DATE(ListChapter.thoi_gian_release, "%B %d, %Y").desc()).first()
		if chapter_new is not None:
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
		else:
			continue
	return data_comedy_comics

#FREE COMICS
async def free_comics():
	data_free_comics = []
	free_comics = ListManga.query.order_by(cast(ListManga.so_luong_view, Integer).desc()).limit(20).all()
	for free_comic in free_comics:
		chapter_new = ListChapter.query.filter_by(id_manga=free_comic.id_manga).order_by(
			func.STR_TO_DATE(ListChapter.thoi_gian_release, "%B %d, %Y").desc()).first()
		if chapter_new is not None:
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
		else:
			continue
	return data_free_comics

#COOMING SOON COMICS
async def cooming_soon_comics():
	data_cooming_soon_comics = []
	cooming_soon_comics = ListManga.query.order_by(cast(ListManga.so_luong_view, Integer).desc()).limit(20).all()
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
	return data_cooming_soon_comics

#RECOMMENDED COMICS
async def recommended_comics():
	data_recommended_comics = []
	recommended_comics = ListManga.query.order_by(cast(ListManga.so_luong_view, Integer).desc()).limit(20).all()
	for recommended_comic in recommended_comics:
		chapter_new = ListChapter.query.filter_by(id_manga=recommended_comic.id_manga)\
			.order_by(func.STR_TO_DATE(ListChapter.thoi_gian_release, "%B %d, %Y").desc()).first()
		if chapter_new is not None:
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
		else:
			continue

#RECENT COMICS
async def recent_comics():
	data_recent_comics = []
	recent_comics = ListManga.query.order_by(cast(ListManga.so_luong_view, Integer).desc()).limit(20).all()
	for recent_comic in recent_comics:
		chapter_new = ListChapter.query.filter_by(id_manga=recent_comic.id_manga) \
			.order_by(func.STR_TO_DATE(ListChapter.thoi_gian_release, "%B %d, %Y").desc()).first()
		if chapter_new is not None:
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

		else:
			continue
	return data_recent_comics

#NEW RELEASE COMICS
async def new_release_comics():
	data_new_release_comics = []
	new_release_comics = ListManga.query.order_by(cast(ListManga.so_luong_view, Integer).desc()).limit(20).all()
	for new_release_comic in new_release_comics:
		chapter_new = ListChapter.query.filter_by(id_manga=new_release_comic.id_manga) \
			.order_by(func.STR_TO_DATE(ListChapter.thoi_gian_release, "%B %d, %Y").desc()).first()
		if chapter_new is not None:
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
		else:
			continue
	return data_new_release_comics