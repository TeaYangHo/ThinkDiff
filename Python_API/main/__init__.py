from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()
def convert_time(time_register):
	time_now = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
	register_date = datetime.strptime(time_register, "%H:%M:%S %d-%m-%Y")
	current_date = datetime.strptime(time_now, "%H:%M:%S %d-%m-%Y")

	participation_time = current_date - register_date
	if participation_time < timedelta(minutes=1):
		time_in_seconds = participation_time.seconds
		time = f"{time_in_seconds} seconds ago"
	elif participation_time < timedelta(hours=1):
		time_in_minutes = participation_time.seconds // 60
		time = f"{time_in_minutes} minute ago"
	elif participation_time < timedelta(days=1):
		time_in_hours = participation_time.seconds // 3600
		time = f"{time_in_hours} hours ago"
	elif participation_time < timedelta(days=2):
		time = f"Yesterday, " + register_date.strftime("%I:%M %p")
	else:
		time = register_date.strftime("%b %d, %I:%M %p")
	return time
#
# a = convert_time("10:30:25 24-07-2023")
#
# print(a)
# import uuid
#
# # Tạo UUID từ chuỗi định danh duy nhất (cần nhập một chuỗi ngẫu nhiên hoặc định danh duy nhất)
# unique_id = "your_unique_id_here"
# new_uuid = uuid.uuid5(uuid.NAMESPACE_OID, unique_id)
#
# print(new_uuid)

