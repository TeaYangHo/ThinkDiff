import asyncio, json, random
import mysql.connector
from urllib.parse import unquote

def conver_url(url):
	if url.endswith(".html"):
		result = url.split("/")[-1].replace(".html", "")
	elif url.endswith("/"):
		result = url.split("/")[-2]
	elif url.endswith("/all-pages"):
		result = url.split("/")[-2]
	else:
		result = url.split("/")[-1]
	result = unquote(result)
	return result

async def insertMangaIntoTable(id_manga, path_segment_manga, title_manga, descript_manga, poster_upload, poster_original,
							detail_manga, categories, chapters, rate, views_original, status, author, id_server):
	connect_mysql = mysql.connector.connect(host="localhost", user="root", password=password, db="MANGASYSTEM")
	cursor = connect_mysql.cursor()
	try:
		mysql_insert_with_param = """
		INSERT INTO List_Manga
		(id_manga, path_segment_manga, title_manga, descript_manga, poster_upload, poster_original,
							detail_manga, categories, chapters, rate, views_original, status, author, id_server) 
		VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
		"""
		data_tuple = (id_manga, path_segment_manga, title_manga, descript_manga, poster_upload, poster_original,
							detail_manga, categories, chapters, rate, views_original, status, author, id_server)
		cursor.execute(mysql_insert_with_param, data_tuple)
		connect_mysql.commit()
		print(f"Inserted manga successfully data into table. {id_manga}")
	except mysql.connector.Error as error:
		print(f"Failed to insert Python variable into mysql table. {id_manga}", error)

	finally:
		if connect_mysql:
			connect_mysql.close()
			print("The mysql connection is closed")


async def insert_Manga_Update_Into_Table(id_manga, path_segment_manga, title_manga, poster, categories, rate):
	connect_mysql = mysql.connector.connect(host="localhost", user="root", password=password, db="MANGASYSTEM")
	cursor = connect_mysql.cursor()
	try:
		mysql_insert_with_param = """
		INSERT INTO Manga_Update
		(id_manga, path_segment_manga, title_manga, poster, categories, rate) 
		VALUES (%s, %s, %s, %s, %s, %s);
		"""
		data_tuple = (id_manga, path_segment_manga, title_manga, poster, categories, rate)
		cursor.execute(mysql_insert_with_param, data_tuple)
		connect_mysql.commit()
		print(f"Inserted manga successfully data into table. {id_manga}")
	except mysql.connector.Error as error:
		print(f"Failed to insert Python variable into mysql table. {id_manga}", error)

	finally:
		if connect_mysql:
			connect_mysql.close()
			print("The mysql connection is closed")


async def start_insert_list_manga(_LINK_DATA_MANGA):
	with open(_LINK_DATA_MANGA, 'r', encoding='utf-8') as f:
		data = json.load(f)
	i = 1
	for manga in data:
		id_manga = manga['ID_Manga']
		path_segment_manga = conver_url(manga['ID_Manga'])
		title_manga = manga['Title_Manga']
		descript_manga = manga['DescriptManga']
		poster_upload = manga['LinkImagePoster_link_Upload']
		poster_original = manga['LinkImagePoster_linkgoc']
		detail_manga = manga['Link_Detail_Manga']
		categories = manga['ListCategories']
		chapters = manga['ListChapter']
		rate = manga['Rate']
		views_original = manga['SoLuongView']
		status = manga['Status']
		author = manga['Tac_Gia']
		id_server = manga['id_Server']

		if id_server not in ("https://www.novelhall.com", "https://bestlightnovel.com/"):

			await insertMangaIntoTable(id_manga, path_segment_manga, title_manga, descript_manga, poster_upload, poster_original,
							detail_manga, categories, chapters, rate, views_original, status, author, id_server)

			await insert_Manga_Update_Into_Table(id_manga, path_segment_manga, title_manga, poster_original, categories, rate)
		else:
			print("Novel")

		print(len(data) - len(data) + i)
		if i % 1000 == 0:
			print("Wait 15s")
			await asyncio.sleep(15)
		i += 1
	print("Done")

async def insert_Chapter_Into_Table(id_chapter, title_chapter, path_segment_chapter, id_manga, time_release):
	connect_mysql = mysql.connector.connect(host="localhost", user="root", password=password, database="MANGASYSTEM")
	cursor = connect_mysql.cursor()

	try:
		mysql_insert_with_param = """
		INSERT INTO List_Chapter
		(id_chapter, title_chapter, path_segment_chapter, id_manga, time_release)
		VALUES (%s, %s, %s, %s, %s);
		"""
		data_tuple = (id_chapter, title_chapter, path_segment_chapter, id_manga, time_release)
		cursor.execute(mysql_insert_with_param, data_tuple)
		connect_mysql.commit()
		print(f"Inserted chapter successfully data into table. {id_chapter}")
		cursor.close()
	except mysql.connector.Error as error:
		print(f"Failed to insert Python variable into mysql table. {id_chapter}", error)
	finally:
		if connect_mysql:
			connect_mysql.close()
			print("The mysql connection is closed")

async def insert_Image_Chapter_Into_Table(path_segment, id_chapter, image_chapter_upload, image_chapter_original):
	connect_mysql = mysql.connector.connect(host="localhost", user="root", password=password, database="MANGASYSTEM")
	cursor = connect_mysql.cursor()

	try:
		mysql_insert_with_param = """
		INSERT INTO Imaga_Chapter
		(path_segment, id_chapter, image_chapter_upload, image_chapter_original)
		VALUES (%s, %s, %s, %s);
		"""
		data_tuple = (path_segment, id_chapter, image_chapter_upload, image_chapter_original)
		cursor.execute(mysql_insert_with_param, data_tuple)
		connect_mysql.commit()
		print(f"Inserted image chapter successfully data into table. {id_chapter}")
		cursor.close()
	except mysql.connector.Error as error:
		print(f"Failed to insert Python variable into mysql table. {id_chapter}", error)
	finally:
		if connect_mysql:
			connect_mysql.close()
			print("The mysql connection is closed")
			
async def update_Manga_Into_Table(id_manga, id_chapter, title_chapter, path_segment, time_release,
								  views_week, views_month, views):
	connect_mysql = mysql.connector.connect(host="localhost", user="root", password=password, database="MANGASYSTEM")
	cursor = connect_mysql.cursor()
	try:
		mysql_update_with_param = """
		UPDATE Manga_Update
		SET id_chapter = %s, title_chapter = %s, path_segment = %s, time_release = %s, 
			views_week = %s, views_month = %s, views = %s
		WHERE id_manga = %s;
		"""
		data_tuple = (id_chapter, title_chapter, path_segment, time_release, views_week, views_month, views, id_manga)
		cursor.execute(mysql_update_with_param, data_tuple)
		connect_mysql.commit()
		print(f"Update chapter successfully data into table. {id_chapter}")
		cursor.close()
	except mysql.connector.Error as error:
		print(f"Failed to Update Python variable into mysql table. {id_chapter}", error)
	finally:
		if connect_mysql:
			connect_mysql.close()
			print("The mysql connection is closed")

async def start_insert_list_chapter(_LINK_DATA_CHAPTER):
	with open(_LINK_DATA_CHAPTER, 'r', encoding='utf-8') as f:
		data = json.load(f)

	i = 1
	for chapter in data:
		id_chapter = chapter["id_chapter"]
		title_chapter = "Chapter ..."
		path_segment_chapter = conver_url(chapter["id_chapter"])
		id_manga = chapter["id_manga"]
		path_segment_manga = conver_url(chapter['id_manga'])
		path_segment = f"{path_segment_chapter}-{path_segment_manga}"
		image_chapter_upload = chapter["list_image_chapter_da_upload"]
		image_chapter_original = chapter["list_image_chapter_server_goc"]
		time_release = chapter["thoi_gian_release"]

		random_3 = random.randint(100, 999)
		random_4 = random.randint(1000, 9999)
		random_5 = random.randint(10000, 99999)
		views_week = random_3
		views_month = random_4
		views = random_5

		await insert_Chapter_Into_Table(id_chapter, title_chapter, path_segment_chapter, id_manga, time_release)
		await insert_Image_Chapter_Into_Table(path_segment, id_chapter, image_chapter_upload, image_chapter_original)
		await update_Manga_Into_Table(id_manga, id_chapter, title_chapter, path_segment, time_release,
									  views_week, views_month, views)

		print(len(data) - len(data) + i)
		if i % 1000 == 0:
			print("Wait 15s")
			await asyncio.sleep(15)
		i += 1
	print("Done")
	
async def start():
	# _LINK_DATA_MANGA = r"/mnt/d/Code Python/ThinkDiff/mysql_anime_manga/data/ListManga.json"
	# _LINK_DATA_CHAPTER = r"/mnt/d/Code Python/ThinkDiff/mysql_anime_manga/data/sssssCopy.json"
	_LINK_DATA_MANGA = r"/root/son/mangareader/truyen-tranh/manga-system/ListManga.json"
	_LINK_DATA_CHAPTER = r"/root/son/mangareader/truyen-tranh/manga-system/ListChapter.json"
	await start_insert_list_manga(_LINK_DATA_MANGA)
	await start_insert_list_chapter(_LINK_DATA_CHAPTER)

# password = ""
password = "mcso@123#@!"
asyncio.run(start())
