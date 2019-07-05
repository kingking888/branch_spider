search_url = "https://so.quandashi.com/search/search/search-list"
verify_url = "https://so.quandashi.com/index/ans"
gt_url = "https://so.quandashi.com/index/abc"
base_detail_url = "https://so.quandashi.com/index/searchdetail/{}.html"

base_search_data = {
    "key": "16475234",
    "param": "0",
    "page": "0",
    "pageSize": "20",
    "styles": "all,jingzhun,high_low_similar,bufen,jiazi,jianzi,bianzi,huanxu,pinyin,teshuzi,xingjinzi",
    "typeCode": "",
    "processCode3": "",
    "createYear": "",
    "groupFilter": "",
    "serviceGoods": "",
    "advanceFilter": "",
    "appkey": "",
    "host": "www.quandashi.com",
    "graphcode": "",
    "similar_code": "",
    "standard_code": "",
    "applicant": "",
}


# redis ===================================================================
REDISHOST, REDISPORT, REDISPASSWORD = "127.0.0.1", "6379", "123456"
# REDISHOST, REDISPORT, REDISPASSWORD = "127.0.0.1", "6379", "123456"
REDISKEY = "branch_qds"
WRONGKEY = "qds_missed"
COOKIEKEY = "qds_cookies"


# mongo ===================================================================
MOGO_DB = "bj_spider"
MONGO_COLL = "xsp_branch_detail_qds"
