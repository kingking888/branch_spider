from pymongo import MongoClient
import pymongo
import re


def get_database_db():
    mongo_client = MongoClient(host="127.0.0.1", port=27017, connect=False)
    db = mongo_client.spider
    return db


def get_local_db():
    mongo_client = MongoClient(host="127.0.0.1", port=27017, connect=False)
    db = mongo_client.xsp
    return db


def get_31_db():
    mongo_client = MongoClient(host="127.0.0.1", port=27017, connect=False)
    return mongo_client

    pass
