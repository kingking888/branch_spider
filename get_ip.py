import requests
from redis import StrictRedis
import time
from conf import REDISHOST, REDISPORT, REDISPASSWORD

client = StrictRedis(host=REDISHOST, port=REDISPORT,
                     password=REDISPASSWORD, db=10)


def get_ip_from_redis():
    """从redis直接取ip"""
    while True:
        try:
            key = client.randomkey()
            ip = client.get(key)
            ip = ip.decode()
            print("IP: ", ip)
            return key, ip
        except Exception as e:
            time.sleep(2)
        pass


def delete_ip(key):
    ip_num = client.dbsize()
    if ip_num > 50:
        try:
            client.delete(key)
        except Exception as e:
            pass


def get_ip_from_url():
    """地址接取ip"""
    url = 'http://127.0.0.1:1316/getIp'
    # url = 'http://127.0.0.1:1319/getIp'
    print("get ip list")
    while True:
        try:
            res = requests.get(url, timeout=5)
            break
        except Exception as e:
            pass
    # ip_list = res.json()
    ip_ = res.content.decode()
    print(ip_)
    return ip_
