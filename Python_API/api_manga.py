from main import *

@app.route("/manga/<path_segment_manga>/")
def get_manga(path_segment_manga):
	manga = List_Manga.query.filter_by(path_segment_manga=path_segment_manga).first()

	if manga is None:
		return jsonify(msg="Manga does not exist!"), 404

	localhost = split_join(request.url)
	chapters = list_chapter(localhost, manga.id_manga, path_segment_manga)

	manga_info = {
		"id_manga": manga.id_manga,
		"title": manga.title_manga,
		"description": manga.descript_manga,
		"poster": manga.poster_original,
		"categories": manga.categories,
		"rate": manga.rate,
		"views": manga.views_original,
		"status": manga.status,
		"author": manga.author,
		"comments": get_comments(path_segment_manga),
		"chapters": chapters
	}

	return jsonify(manga_info)



@app.route("/manga/<path_segment_manga>/<path_segment_chapter>/")
def get_image_chapter(path_segment_manga, path_segment_chapter):
	path_segment = f"{path_segment_manga}-{path_segment_chapter}"
	chapters = Imaga_Chapter.query.filter_by(path_segment=path_segment).first()

	if chapters is None:
		return jsonify(msg="NONE"), 404

	image_chapter = chapters.image_chapter_original.split(",")
	chapter = List_Chapter.query.filter_by(id_chapter=chapters.id_chapter).first()
	manga = Manga_Update.query.filter_by(id_manga=chapter.id_manga).first()

	if current_user.is_authenticated:
		id_user = current_user.id_user
		profile = Profiles.query.filter_by(id_user=id_user).first()
		profile.number_reads += 1

	manga.views_week += 1
	manga.views_month += 1
	manga.views += 1
	db.session.commit()
	return jsonify(ImageChapter=image_chapter)

# COMMENT CHAPTER MANGA
@app.route("/manga/<path_segment_manga>/<path_segment_chapter>/", methods=["POST"])
@login_required
def comment_chapter(path_segment_manga, path_segment_chapter):
	form = CommentsForm()
	id_user = current_user.id_user
	profile = Profiles.query.get_or_404(id_user)

	manga = List_Manga.query.filter_by(path_segment_manga=path_segment_manga).first()
	if manga is None:
		return jsonify(message="Manga not found"), 404

	chapter = List_Chapter.query.filter_by(id_manga=manga.id_manga, path_segment_chapter=path_segment_chapter).first()
	if chapter is None:
		return jsonify(message="Chapter not found"), 404

	if form.validate_on_submit():
		content = form.content.data

		time = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
		comment = Comments(id_user=id_user, path_segment_manga=path_segment_manga,
							path_segment_chapter=path_segment_chapter, content=content, time_comment=time)
		profile.number_comments += 1
		db.session.add(comment)
		db.session.commit()
		responses = {
			"id_user": id_user,
			"name_user": profile.name_user,
			"avatar_user": profile.avatar_user,
			"chapter": path_segment_chapter,
			"content": content,
			"time_comment": convert_time(time)
		}
		return jsonify(responses=responses)
	return jsonify(error=form.errors), 400

# COMMENT MANGA
@app.route("/manga/<path_segment_manga>/", methods=["POST"])
@login_required
def comment_manga(path_segment_manga):
	form = CommentsForm()
	id_user = current_user.id_user
	profile = Profiles.query.get_or_404(id_user)

	manga = List_Manga.query.filter_by(path_segment_manga=path_segment_manga).first()
	if manga is None:
		return jsonify(message="Manga not found"), 404

	if form.validate_on_submit():
		content = form.content.data

		path_segment_chapter = "NONE"

		time = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
		comment = Comments(id_user=id_user, path_segment_manga=path_segment_manga,
							path_segment_chapter=path_segment_chapter, content=content, time_comment=time)
		profile.number_comments += 1
		db.session.add(comment)
		db.session.commit()
		responses = {
			"id_user": id_user,
			"name_user": profile.name_user,
			"avatar_user": profile.avatar_user,
			"chapter": path_segment_chapter,
			"content": content,
			"time_comment": convert_time(time)
		}
		return jsonify(responses=responses)
	return jsonify(error=form.errors), 400


@app.route("/reply-comment/<id_comment>/", methods=["POST"])
@login_required
def reply_comments(id_comment):
	form = CommentsForm()
	id_user = current_user.id_user
	profile = Profiles.query.get_or_404(id_user)
	comments = Comments.query.get_or_404(id_comment)
	if form.validate_on_submit():
		content = form.content.data
		time = datetime.now().strftime("%H:%M:%S %d-%m-%Y")

		comment = Comments(id_user=id_user, content=content, time_comment=time,
						   path_segment_manga=comments.path_segment_manga, path_segment_chapter=comments.path_segment_chapter,
						   is_comment_reply=True, reply_id_comment=id_comment)

		db.session.add(comment)
		db.session.commit()
		responses = {
			"id_user": id_user,
			"name_user": profile.name_user,
			"avatar_user": profile.avatar_user,
			"content": content,
			"chapter": comments.path_segment_chapter,
			"time_comment": convert_time(time),
			"is_comment_reply": True,
			"reply_id_comment": id_comment

		}
		return jsonify(responses=responses)
	return jsonify(error=form.errors), 400


@app.route("/delete-comment/<id_comment>/", methods=["DELETE"])
def delete_comment(id_comment):
	id_user = current_user.id_user
	comment = Comments.query.get_or_404(id_comment)

	if comment.id_user != id_user:
		return jsonify(error="You do not have permission to delete comment"), 400

	comment_diary = CommentDiary(id_comment=comment.id_comment, content=comment.content,
								 comment_type="delete", time_comment=comment.time_comment)
	db.session.add(comment_diary)

	LikesComment.query.filter_by(id_comment=id_comment).delete()

	delete_reply_comment(comment)
	db.session.delete(comment)
	db.session.commit()
	return jsonify(message="Comment deleted successfully")

@app.route("/edit-comment/<id_comment>/", methods=["PATCH"])
@login_required
def edit_comments(id_comment):
	form = CommentsForm()
	id_user = current_user.id_user
	profile = Profiles.query.get_or_404(id_user)
	comments = Comments.query.get_or_404(id_comment)

	if comments.id_user != id_user:
		return jsonify(error="You do not have permission to edit comment"), 400

	if form.validate_on_submit():
		content = form.content.data
		time = datetime.now().strftime("%H:%M:%S %d-%m-%Y")

		if comments.is_edited_comment == False:
			comment = CommentDiary(id_comment=id_comment, content=comments.content, comment_type="before", time_comment=comments.time_comment)
			db.session.add(comment)
			db.session.commit()

		comments.content = content
		edit_comment = CommentDiary(id_comment=id_comment, content=content, comment_type="after", time_comment=time)
		db.session.add(edit_comment)

		comments.is_edited_comment = True
		db.session.commit()
		responses = {
			"id_user": id_user,
			"name_user": profile.name_user,
			"avatar_user": profile.avatar_user,
			"chapter": comments.path_segment_chapter,
			"content_update": content,
			"time_comment": convert_time(comments.time_comment)
		}
		return jsonify(responses=responses)
	return jsonify(error=form.errors), 400

@app.route("/comment-diary/<id_comment>/")
@login_required
def comments_diary(id_comment):
	id_user = current_user.id_user
	profile = Profiles.query.get_or_404(id_user)
	comment = Comments.query.get_or_404(id_comment)
	comments = CommentDiary.query.filter_by(id_comment=id_comment).order_by(func.STR_TO_DATE(CommentDiary.time_comment, "%H:%i:%S %d-%m-%Y").asc()).all()
	responses = []
	for comm in comments:
		result = {
			"id_user": id_user,
			"name_user": profile.name_user,
			"avatar_user": profile.avatar_user,
			"chapter": comment.path_segment_chapter,
			"content": comm.content,
			"time_comment": convert_time(comm.time_comment)
		}
		responses.append(result)
	return jsonify(CommentDiary=responses)

@app.route("/like-comment/<id_comment>/", methods=["POST", "PATCH"])
@login_required
def like_comment(id_comment):
	id_user = current_user.id_user
	like_status = LikesComment.query.filter_by(id_comment=id_comment, id_user=id_user).first()
	comment = Comments.query.filter_by(id_comment=id_comment).first()
	if not comment:
		return jsonify(message="Comment does not exist!"), 404
	if like_status:
		if like_status.status == "like":
			like_status.status = "cancel"
			db.session.commit()
			return jsonify(message="Cancel liked Comment  successfully")
		else:
			like_status.status = "like"
			db.session.commit()
			return jsonify(message="Liked comment successfully")
	else:
		new_like = LikesComment(id_comment=id_comment, id_user=id_user, status="like")
		db.session.add(new_like)
		db.session.commit()
		return jsonify(message="Liked comment successfully")
