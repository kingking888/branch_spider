from mongo_api import get_local_db
from redis_api import connection
from conf import REDISKEY

redis_ = connection()

db = get_local_db()["gov_spider"]

datas = db.find(no_cursor_timeout=True).batch_size(100)
for data in datas:
    print(data["id"])
    redis_.sadd(REDISKEY, data["id"])
