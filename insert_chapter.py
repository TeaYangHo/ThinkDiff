import asyncio, json
import mysql.connector



async def insertChapterIntoTable(id_chapter, title_chapter, id_manga, list_image_chapter_da_upload, list_image_chapter_server_goc,
																time_release):
	connect_mysql = mysql.connector.connect(host="localhost", user="root", password="", database="MANGASYSTEM")
	cursor = connect_mysql.cursor()

	try:
		sqlite_insert_with_param = """
		INSERT INTO LISTCHAPTER
		(id_chapter, title_chapter, id_manga, list_image_chapter_da_upload, list_image_chapter_server_goc, time_release)
		VALUES (%s, %s, %s, %s, %s, %s);
		"""
		data_tuple = (
		id_chapter, title_chapter, id_manga, list_image_chapter_da_upload, list_image_chapter_server_goc, time_release)
		cursor.execute(sqlite_insert_with_param, data_tuple)
		connect_mysql.commit()
		print(f"Inserted chapter successfully data into table. {id_chapter}")
		cursor.close()
	except mysql.connector.Error as error:
		print("Failed to insert Python variable into sqlite table", error)
	finally:
		if connect_mysql:
			connect_mysql.close()
			print("The SQLite connection is closed")

async def update_New_Manga_Information_IntoTable(id_manga, id_chapter, title_chapter, time_release):
	connect_mysql = mysql.connector.connect(host="localhost", user="root", password="", database="MANGASYSTEM")
	cursor = connect_mysql.cursor()
	try:
		sqlite_update_with_param = """
		UPDATE Manga_Information_New
		SET id_chapter = %s, title_chapter = %s, time_release = %s
		WHERE id_manga = %s;
		"""
		data_tuple = (id_chapter, title_chapter, time_release, id_manga)
		cursor.execute(sqlite_update_with_param, data_tuple)
		connect_mysql.commit()
		print(f"Update chapter successfully data into table. {id_chapter}")
		cursor.close()
	except mysql.connector.Error as error:
		print("Failed to Update Python variable into sqlite table", error)
	finally:
		if connect_mysql:
			connect_mysql.close()
			print("The SQLite connection is closed")

async def start_insert_list_chapter(_LINK_DATA_CHAPTER):
	with open(_LINK_DATA_CHAPTER, 'r', encoding='utf-8') as f:
		data = json.load(f)

	i = 1
	for chapter in data:
		id_chapter = chapter["id_chapter"]
		title_chapter = "Chapter ..."
		id_manga = chapter["id_manga"]
		list_image_chapter_da_upload = chapter["list_image_chapter_da_upload"]
		list_image_chapter_server_goc = chapter["list_image_chapter_server_goc"]
		time_release = chapter["thoi_gian_release"]
		await insertChapterIntoTable(id_chapter, title_chapter, id_manga, list_image_chapter_da_upload, list_image_chapter_server_goc, time_release)
		await update_New_Manga_Information_IntoTable(id_manga, id_chapter, title_chapter, time_release)

		print(len(data) - len(data) + i)
		if i % 1000 == 0:
			print("Wait 15s")
			await asyncio.sleep(15)
		i += 1

	print("Done")
async def start():
	_LINK_DATA_CHAPTER = r"/mnt/d/Code Python/ThinkDiff/mysql_anime_manga/data/sssssCopy.json"
	await start_insert_list_chapter(_LINK_DATA_CHAPTER)
asyncio.run(start())
