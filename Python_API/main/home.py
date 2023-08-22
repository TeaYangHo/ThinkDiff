from . import *

#NEW RELEASE COMICS
def new_release_comics(limit):
	data_new_release_comics = []
	new_release_comics = (Manga_Update.query.
						  order_by(func.STR_TO_DATE(Manga_Update.time_release, "%b %d, %Y").desc()).limit(limit).all())
	for new_release_comic in new_release_comics:
		localhost = split_join(request.url)
		data = {
			"url_manga": make_link(localhost, f"/manga/{new_release_comic.path_segment_manga}"),
			"title_manga": new_release_comic.title_manga,
			"image_poster_link_goc": new_release_comic.poster,
			"rate": new_release_comic.rate,
			"chapter_new": new_release_comic.title_chapter,
			"url_chapter": make_link(localhost,f"/manga/{new_release_comic.path_segment_manga}/{new_release_comic.path_segment_chapter}"),
			"time_release": new_release_comic.time_release
		}
		data_new_release_comics.append(data)

	return data_new_release_comics

#RECENT COMICS
def recent_comics(limit):
	data_recent_comics = []
	recent_comics = (Manga_Update.query.
					 order_by(func.STR_TO_DATE(Manga_Update.time_release, "%b %d, %Y").desc()).limit(limit).all())
	for recent_comic in recent_comics:
		localhost = split_join(request.url)
		data = {
			"url_manga": make_link(localhost, f"/manga/{recent_comic.path_segment_manga}"),
			"title_manga": recent_comic.title_manga,
			"image_poster_link_goc": recent_comic.poster,
			"rate": recent_comic.rate,
			"chapter_new": recent_comic.title_chapter,
			"url_chapter": make_link(localhost,
										f"/manga/{recent_comic.path_segment_manga}/{recent_comic.path_segment_chapter}"),
			"time_release": recent_comic.time_release
		}
		data_recent_comics.append(data)

	return data_recent_comics

#RECOMMENDED COMICS
def recommended_comics(limit):
	data_recommended_comics = []
	recommended_comics = (Manga_Update.query.
						  order_by(func.STR_TO_DATE(Manga_Update.time_release, "%b %d, %Y").desc()).limit(limit).all())
	for recommended_comic in recommended_comics:
		localhost = split_join(request.url)
		data = {
			"url_manga": make_link(localhost, f"/manga/{recommended_comic.path_segment_manga}"),
			"title_manga": recommended_comic.title_manga,
			"image_poster_link_goc": recommended_comic.poster,
			"rate": recommended_comic.rate,
			"chapter_new": recommended_comic.title_chapter,
			"url_chapter": make_link(localhost,
										f"/manga/{recommended_comic.path_segment_manga}/{recommended_comic.path_segment_chapter}"),
			"time_release": recommended_comic.time_release
		}
		data_recommended_comics.append(data)
	return data_recommended_comics

#COOMING SOON COMICS
def cooming_soon_comics(limit):
	data_cooming_soon_comics = []
	cooming_soon_comics = (Manga_Update.query.
						   order_by(func.STR_TO_DATE(Manga_Update.time_release, "%b %d, %Y").desc()).limit(limit).all())
	for cooming_soon_comic in cooming_soon_comics:
		data = {
			"title_manga": cooming_soon_comic.title_manga,
			"image_poster_link_goc": cooming_soon_comic.poster,
			"author": "AUTHOR",
			"categories": cooming_soon_comic.categories,
			"time_release": cooming_soon_comic.time_release
		}
		data_cooming_soon_comics.append(data)
	return data_cooming_soon_comics

# BEST 15 COMICS WEEK
def best_15_comics_week(limit):
	data_best_15_comics_weeks = []
	best_15_comics_weeks = (Manga_Update.query.
							order_by(func.STR_TO_DATE(Manga_Update.time_release, "%b %d, %Y").desc()).limit(limit).all())
	for best_15_comics_week in best_15_comics_weeks:
		localhost = split_join(request.url)
		data = {
			"url_manga": make_link(localhost, f"/manga/{best_15_comics_week.path_segment_manga}"),
			"title_manga": best_15_comics_week.title_manga,
			"image_poster_link_goc": best_15_comics_week.poster,
			"rate": best_15_comics_week.rate,
			"chapter_new": best_15_comics_week.title_chapter,
			"url_chapter": make_link(localhost,
										   f"/manga/{best_15_comics_week.path_segment_manga}/{best_15_comics_week.path_segment_chapter}"),
			"time_release": best_15_comics_week.time_release
		}
		data_best_15_comics_weeks.append(data)
	return data_best_15_comics_weeks

#COMEDY COMMICS
def comedy_comics(limit):
	data_comedy_comics = []
	comedy_comics = (Manga_Update.query.filter(Manga_Update.categories.like('%Comedy%')).
					 order_by(func.STR_TO_DATE(Manga_Update.time_release, "%b %d, %Y").desc()).limit(limit).all())
	for comedy_comic in comedy_comics:
		localhost = split_join(request.url)
		data = {
			"url_manga": make_link(localhost, f"/manga/{comedy_comic.path_segment_manga}"),
			"title_manga": comedy_comic.title_manga,
			"image_poster": comedy_comic.poster,
			"rate": comedy_comic.rate,
			"chapter_new": comedy_comic.title_chapter,
			"url_chapter": make_link(localhost,
										f"/manga/{comedy_comic.path_segment_manga}/{comedy_comic.path_segment_chapter}"),
			"time_release": comedy_comic.time_release
		}
		data_comedy_comics.append(data)
	return data_comedy_comics

#FREE COMICS
def free_comics(limit):
	data_free_comics = []
	free_comics = (Manga_Update.query.
				   order_by(func.STR_TO_DATE(Manga_Update.time_release, "%b %d, %Y").desc()).limit(limit).all())
	for free_comic in free_comics:
		localhost = split_join(request.url)
		data = {
			"url_manga": make_link(localhost, f"/manga/{free_comic.path_segment_manga}"),
			"title_manga": free_comic.title_manga,
			"image_poster_link_goc": free_comic.poster,
			"rate": free_comic.rate,
			"chapter_new": free_comic.title_chapter,
			"url_chapter": make_link(localhost,
										f"/manga/{free_comic.path_segment_manga}/{free_comic.path_segment_chapter}"),
			"time_release": free_comic.time_release
		}
		data_free_comics.append(data)
	return data_free_comics

# NEWS
def anime_manga_news(limit):
	data_news = []
	news = (Anime_Manga_News.query
			.order_by(func.STR_TO_DATE(Anime_Manga_News.time_news, "%b %d, %h:%i %p").desc()).limit(limit).all())
	localhost = split_join(request.url)
	for new in news:
		id_news = conver_url(new.idNews)
		data = {
			"id_news": id_news,
			"url_news": make_link(localhost, f"/news/{id_news}"),
			"title_news": new.title_news,
			"time_news": new.time_news,
			"images_poster": new.images_poster,
		}
		data_news.append(data)
	return data_news

# NEW USER
def user_new(limit):
	users = Users.query.order_by(func.STR_TO_DATE(Users.time_register, "%H:%i:%S %d-%m-%Y").desc()).limit(limit).all()
	data_user = []
	for user in users:
		profile = Profiles.query.filter_by(id_user=user.id_user).first()
		data = {
			"id_user": user.id_user,
			"name_user": profile.name_user,
			"avatar_user": profile.avatar_user,
			"participation_time": convert_time(user.time_register)
		}
		data_user.append(data)
	return data_user

#RANK WEEK
def rank_manga_week(limit):
	data_rank_manga_week = []
	rank_manga_week = Manga_Update.query.order_by(Manga_Update.views_week.desc()).limit(limit).all()
	for rank in rank_manga_week:
		localhost = split_join(request.url)
		data = {
			
			"url_manga": make_link(localhost, f"/manga/{rank.path_segment_manga}"),
			"title_manga": rank.title_manga,
			"image_poster": rank.poster,
			"categories": rank.categories,
			"views_week": rank.views_week
		}
		data_rank_manga_week.append(data)
	return data_rank_manga_week

#RANK MONTH
def rank_manga_month(limit):
	data_rank_manga_month = []
	rank_manga_month = Manga_Update.query.order_by(Manga_Update.views_month.desc()).limit(limit).all()
	for rank in rank_manga_month:
		localhost = split_join(request.url)
		data = {
			
			"url_manga": make_link(localhost, f"/manga/{rank.path_segment_manga}"),
			"title_manga": rank.title_manga,
			"image_poster": rank.poster,
			"categories": rank.categories,
			"views_month": rank.views_month
		}
		data_rank_manga_month.append(data)
	return data_rank_manga_month

#RANK YEAR
def rank_manga_year(limit):
	data_rank_manga_year = []
	rank_manga_year = Manga_Update.query.order_by(Manga_Update.views.desc()).limit(limit).all()
	for rank in rank_manga_year:
		localhost = split_join(request.url)
		data = {
			
			"url_manga": make_link(localhost, f"/manga/{rank.path_segment_manga}"),
			"title_manga": rank.title_manga,
			"image_poster": rank.poster,
			"categories": rank.categories,
			"views": rank.views
		}
		data_rank_manga_year.append(data)
	return data_rank_manga_year

# COMMENTS
def comment_new(limit):
	data_comment_news = []
	rank_manga = Manga_Update.query.order_by(Manga_Update.views.desc()).limit(limit).all()
	for i, rank in enumerate(rank_manga):
		localhost = split_join(request.url)
		comment_new = (Comments.query.filter_by(path_segment_manga=rank.path_segment_manga)
					.order_by(func.STR_TO_DATE(Comments.time_comment, "%H:%i:%S %d-%m-%Y").desc()).first())
		if comment_new is None:
			continue
		profile = Profiles.query.get_or_404(comment_new.id_user)
		count_comment = Comments.query.filter_by(path_segment_manga=comment_new.path_segment_manga,
												is_comment_reply=False).count()
		count_reply_comment = Comments.query.filter_by(path_segment_manga=comment_new.path_segment_manga,
													is_comment_reply=True).count()
		data = {
			"id_user": comment_new.id_user,
			"name_user": profile.name_user,
			"avatar_user": profile.avatar_user,
			"id_comment": comment_new.id_comment,
			"content": comment_new.content,
			"time_comment": convert_time(comment_new.time_comment),
			"title_manga": rank.title_manga,
			"url_manga": make_link(localhost, f"/manga/{comment_new.path_segment_manga}"),
			"count_comment": count_comment,
			"count_reply_comment": count_reply_comment
		}
		data_comment_news.append(data)
	return data_comment_news

#REVIEWS MANGA
def reviews_manga(limit):
	data_reviews_manga = []
	reviews_manga = (Reviews_Manga.query
					 .order_by(func.STR_TO_DATE(Reviews_Manga.time_review, "%b %d, %Y").desc()).limit(limit).all())

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
def reviews_anime(limit):
	data_reviews_anime = []
	reviews_manga = (Reviews_Anime.query.
					 order_by(func.STR_TO_DATE(Reviews_Anime.time_review, "%b %d, %Y").desc()).limit(limit).all())
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

