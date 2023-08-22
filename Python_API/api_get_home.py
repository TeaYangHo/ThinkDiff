from main import *
from main.home import user_new, anime_manga_news, reviews_manga, reviews_anime, rank_manga_week, rank_manga_month, rank_manga_year
from main.home import comedy_comics, free_comics, cooming_soon_comics, recommended_comics, recent_comics, new_release_comics
from main.home import comment_new, best_15_comics_week

@app.route("/")
@cache.cached(timeout=60)
def get_home():
	result = [
		{"id": 1, "type": 1, "name": "New Release Comics", "data": new_release_comics(20)},
		{"id": 2, "type": 1, "name": "Recent Comics", "data": recent_comics(12)},
		{"id": 3, "type": 1, "name": "Recommended Comics", "data": recommended_comics(12)},
		{"id": 4, "type": 1, "name": "Cooming Soon Comics", "data": cooming_soon_comics(5)},
		{"id": 5, "type": 1, "name": "Top 15 Best Comics Of The Week", "data": best_15_comics_week(15)},
		{"id": 6, "type": 1, "name": "Comedy Comics", "data": comedy_comics(24)},
		{"id": 7, "type": 1, "name": "Free Comics", "data": free_comics(12)},
		{"id": 8, "type": 2, "name": "Anime Manga News", "data": anime_manga_news(7)},
		{"id": 9, "type": 3, "name": "Rank Week", "data": rank_manga_week(20)},
		{"id": 10, "type": 3, "name": "Rank Month", "data": rank_manga_month(20)},
		{"id": 11, "type": 3, "name": "Rank Year", "data": rank_manga_year(20)},
		{"id": 12, "type": 4, "name": "User New", "data": user_new(12)},
		{"id": 13, "type": 4, "name": "Comments", "data": comment_new(10)}
	]
	return result

@app.route("/news/<id_news>/")
def get_news(id_news):
	id_news = f"https://myanimelist.net/news/{id_news}"
	news = Anime_Manga_News.query.filter_by(idNews=id_news).first()
	if news is None:
		return jsonify(mgs="News do not exist!"), 404
	localhost = split_join(request.url)

	comment = []
	comment_news = Comment_News.query.filter_by(id_news=id_news).all()

	for comment_new in comment_news:
		id_user = 1
		profile = Profiles.query.filter_by(id_user=id_user).first()
		data_comment = {
			"id_comment": comment_new.id_comment,
			"id_user": id_user,
			"name_user": profile.name_user,
			"avatar_user": profile.avatar_user,
			"content": comment_new.comment,
			"time_comment": comment_new.time_comment,
			"likes": 0,
			"is_comment_reply": False,
			"is_edited_comment": False,
			"replies": []
		}
		comment.append(data_comment)

	result = {
		"title_news": news.title_news,
		"images_poster": news.images_poster,
		"profile_user_post": make_link(localhost, f"/user/admin-fake"),
		"time_news": news.time_news,
		"category": news.category,
		"descript_pro": news.descript_pro,
		"comment": comment
	}
	return jsonify(result)

@app.route("/new_release_comics/")
@cache.cached(timeout=60)
def see_all_new_release_comics():
	return new_release_comics(None)

@app.route("/recent_comics/")
@cache.cached(timeout=60)
def see_all_recent_comics():
	return recent_comics(None)

@app.route("/recommended_comics/")
@cache.cached(timeout=60)
def see_all_recommended_comics():
	return recommended_comics(None)

@app.route("/cooming_soon_comics/")
@cache.cached(timeout=60)
def see_all_cooming_soon_comics():
	return cooming_soon_comics(None)

@app.route("/best_15_comics_week/")
@cache.cached(timeout=60)
def see_all_best_15_comics_week():
	return best_15_comics_week(None)

@app.route("/comedy_comics/")
@cache.cached(timeout=60)
def see_all_comedy_comics():
	return comedy_comics(None)

@app.route("/free_comics/")
@cache.cached(timeout=60)
def see_all_free_comics():
	return free_comics(None)

@app.route("/anime_manga_news/")
@cache.cached(timeout=60)
def see_all_anime_manga_news():
	return anime_manga_news(None)

@app.route("/user_new/")
@cache.cached(timeout=60)
def see_all_user_new():
	return user_new(None)


@app.route("/rank_manga_week/")
@cache.cached(timeout=600)
def see_all_rank_manga_week():
	return rank_manga_week(None)


@app.route("/rank_manga_month/")
@cache.cached(timeout=600)
def see_all_rank_manga_month():
	return rank_manga_month(None)


@app.route("/rank_manga_year/")
@cache.cached(timeout=600)
def see_all_rank_manga_year():
	return rank_manga_year(None)



