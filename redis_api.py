from redis import StrictRedis
from conf import REDISPORT, REDISHOST, REDISPASSWORD


def connection(db=0):
    clinet = StrictRedis(host=REDISHOST, port=REDISPORT,
                         password=REDISPASSWORD, db=db)

    return clinet


def database_connection(db=0):
    clinet = StrictRedis(
        host="127.0.0.1", port="6379", password="123456", db=0)

    return clinet


if __name__ == '__main__':
    cli = connection()
    import time
    cc = cli.srandmember("qds_cookies")
    cc = cc.decode()
    print(cc)
