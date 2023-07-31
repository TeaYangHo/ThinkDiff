import asyncio, json
import mysql.connector




async def insertMangaIntoTable(id_manga, title_manga, descript_manga, poster_upload, poster_goc,
							   link_detail_manga, list_categories, list_chapter, rate, views, status, author,
							   id_server):
	connect_mysql = mysql.connector.connect(host="localhost", user="root", passwd="", db="MANGASYSTEM")
	cursor = connect_mysql.cursor()
	try:
		sqlite_insert_with_param = """
		REPLACE INTO LISTMANGA
		(id_manga, title_manga, descript_manga, poster_upload, poster_goc, 
		link_detail_manga, list_categories, list_chapter, rate, views, status, author, id_server) 
		VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
		"""
		data_tuple = (id_manga, title_manga, descript_manga, poster_upload, poster_goc,
					  link_detail_manga, list_categories, list_chapter, rate, views, status, author, id_server)
		cursor.execute(sqlite_insert_with_param, data_tuple)
		connect_mysql.commit()
		print(f"Inserted manga successfully data into table. {id_manga}")
	except mysql.connector.Error as error:
		print(f"Failed to insert Python variable into sqlite table. {id_manga}", error)

	finally:
		if connect_mysql:
			connect_mysql.close()
			print("The SQLite connection is closed")


async def insert_New_Manga_Information_IntoTable(id_manga, title_manga, poster, rate):
	connect_mysql = mysql.connector.connect(host="localhost", user="root", passwd="", db="MANGASYSTEM")
	cursor = connect_mysql.cursor()
	try:
		sqlite_insert_with_param = """
		INSERT INTO Manga_Information_New
		(id_manga, title_manga, poster, rate) 
		VALUES (%s, %s, %s, %s);
		"""
		data_tuple = (id_manga, title_manga, poster, rate)
		cursor.execute(sqlite_insert_with_param, data_tuple)
		connect_mysql.commit()
		print(f"Inserted manga successfully data into table. {id_manga}")
	except mysql.connector.Error as error:
		print(f"Failed to insert Python variable into sqlite table. {id_manga}", error)

	finally:
		if connect_mysql:
			connect_mysql.close()
			print("The SQLite connection is closed")


async def start_insert_list_manga(_LINK_DATA_MANGA):
	with open(_LINK_DATA_MANGA, 'r', encoding='utf-8') as f:
		data = json.load(f)
	i = 1
	for manga in data:
		id_manga = manga['ID_Manga']
		title_manga = manga['Title_Manga']
		descript_manga = manga['DescriptManga']
		poster_upload = manga['LinkImagePoster_link_Upload']
		poster_goc = manga['LinkImagePoster_linkgoc']
		link_detail_manga = manga['Link_Detail_Manga']
		list_categories = manga['ListCategories']
		list_chapter = manga['ListChapter']
		rate = manga['Rate']
		views = manga['SoLuongView']
		status = manga['Status']
		author = manga['Tac_Gia']
		id_server = manga['id_Server']
		await insertMangaIntoTable(id_manga, title_manga, descript_manga, poster_upload, poster_goc,
								   link_detail_manga, list_categories, list_chapter, rate, views, status, author,
								   id_server)

		await insert_New_Manga_Information_IntoTable(id_manga, title_manga, poster_goc, rate)
		if i % 1000 == 0:
			print("Wait 15s")
			await asyncio.sleep(10)


		print(len(data) - len(data) + i)
		i += 1
	print("Done")


async def start():
	_LINK_DATA_MANGA = fr"/mnt/d/Code Python/ThinkDiff/mysql_anime_manga/data/ListManga.json"
	await start_insert_list_manga(_LINK_DATA_MANGA)

asyncio.run(start())