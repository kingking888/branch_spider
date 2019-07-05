from conf import search_url, base_search_data, base_detail_url, COOKIEKEY, REDISKEY, WRONGKEY, MONGO_DB, MONGO_COLL
import requests
from get_ip import get_ip_from_url, get_ip_from_redis, delete_ip
from lxml import etree
from ppet_get_cookie import Cookei
from redis_api import connection
import logging
import time
from copy import deepcopy
import datetime
import json
from mongo_api import get_31_db, get_database_db
import re

from logger import setup_logging
setup_logging()
logger = logging.getLogger("quandashi")

s = """Accept: application/json, text/javascript, */*; q=0.01
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
Cache-Control: no-cache
Connection: keep-alive
Host: so.quandashi.com
Pragma: no-cache
User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36
"""


def format_s(s):
    return {item.split(':', 1)[0].strip(): item.split(':', 1)[1].strip() for item in s.split('\n') if item}


bease_headers = format_s(s)


class QanDaShi():

    def __init__(self):
        self.brand_id = None
        self.category = "7"
        self.redis_client = connection()
        self.db = get_database_db()["test_qds"]
        # self.db = get_31_db()[MONGO_DB][MONGO_COLL]
        self.key = None
        self.change_ip()

    def change_ip(self):
        # if self.key:
        #     delete_ip(self.key)
        # self.key, self.ip = get_ip_from_redis()

        # =======================================
        self.ip = get_ip_from_url()
        self.proxies = {
            "http": f"http://{self.ip}",
            "https": f"https://{self.ip}"
        }

    def get_cookie(self):
        """从redis获取验证后的cookie
        加入使用次数和过期时间限制：每个cookie只能成功使用18次，有效时间10分钟
        Returns:
            [cookie] -- [str]
        """
        while True:
            try:
                cookie_data = self.redis_client.spop(COOKIEKEY)
                cookie_data = eval(cookie_data)
                use_count = cookie_data.get("use_count", 0)
                timestamp = cookie_data.get("timestamp", 0)
                now_stamp = time.time()
                if use_count >= 18 or now_stamp - timestamp > 600:
                    self.redis_client.srem(cookie_data)
                    continue
                self.cookie_data = cookie_data
                return cookie_data["cookie"]
            except Exception as e:
                logger.info(e)
                time.sleep(2)
                pass

    def push_back_cookie(self, used=True):
        """将cookie放回redis

        Keyword Arguments:
            used {bool} -- [True表示成功获取了结果，cookie放回的试试需要修改使用次数] (default: {True})
        """
        if used:
            self.cookie_data["use_count"] = self.cookie_data.get(
                "use_count", 0) + 1
            self.redis_client.sadd(COOKIEKEY, json.dumps(self.cookie_data))
        else:
            self.redis_client.sadd(COOKIEKEY, json.dumps(self.cookie_data))

    def get_info(self, url, flag=False):
        headers = deepcopy(bease_headers)
        while True:
            cookie = self.get_cookie()
            headers["Cookie"] = cookie
            try:
                res = requests.get(url, headers=headers,
                                   proxies=self.proxies, timeout=3)
                res.encoding = res.apparent_encoding
                if flag:
                    if flag not in res.text:
                        raise Exception("没有获取待结果！")
                self.push_back_cookie()
                return res
            except Exception as e:
                logger.info(f"{e}, {url}")
                self.push_back_cookie(used=False)
                self.change_ip()

    def post_info(self, url, data, flag=False):
        headers = deepcopy(bease_headers)
        while True:
            try:
                cookie = self.get_cookie()
                headers["Cookie"] = cookie
                # print("代理： ", self.proxies)
                res = requests.post(search_url, data=data,
                                    headers=headers, proxies=self.proxies, timeout=3)
                res.encoding = res.apparent_encoding
                json_res = res.json()
                # print("结果: ", json_res)
                results = json_res.get("data", {}).get(
                    "data", {}).get("items", [])
                if not results:
                    self.push_back_cookie(used=False)
                else:
                    self.push_back_cookie()
                return results
            except Exception as e:
                logger.info(f"{e}, {url}")
                self.push_back_cookie(used=False)
                self.change_ip()

    def extract_data(self, response):
        data = {"sourceId": "qds",
                "regCode": self.brand_id,
                "category": self.category,
                "id": str(self.brand_id) + "_" + str(self.category),
                "intCls": self.category}
        html = etree.HTML(response.text)
        ap_date = html.xpath(
            '//div[@class="page page-detail"]//td[contains(text(), "申请日期")]/following-sibling::td[1]/text()')  # 申请时间
        ap_date = "".join(ap_date)
        data["applyDate"] = ap_date.replace("\n", "").strip()

        brandName = html.xpath(
            '//div[@class="page page-detail"]//td[contains(text(), "商标名称")]/following-sibling::td[1]/text()')  # 商标名称
        brandName = "".join(brandName)
        data["brandName"] = brandName.replace("\n", "").strip()

        applicant_tds = html.xpath(
            '//div[@class="page page-detail"]//td[contains(text(), "申请人名称")]/following-sibling::td')
        applicant_cn = applicant_tds[0].xpath(
            './/text()')  # 申请人中文名
        applicant_cn = "".join(applicant_cn)
        data["applicantCN"] = applicant_cn.replace("\n", "").strip()

        applicant_en = applicant_tds[1].xpath(
            './/text()')  # 申请人英文名
        applicant_en = "".join(applicant_en)
        data["applicantEN"] = applicant_en.replace("\n", "").strip()

        address_tds = html.xpath(
            '//div[@class="page page-detail"]//td[contains(text(), "申请人地址")]/following-sibling::td')
        address_cn = address_tds[0].xpath(
            './/text()')  # 申请人中文地址
        address_cn = "".join(address_cn)
        data["addressCN"] = address_cn.replace("\n", "").strip()

        address_en = address_tds[1].xpath(
            './/text()')  # 申请人英文地址
        address_en = "".join(address_en)
        data["addressEN"] = address_en.replace("\n", "").strip()

        announcement_issue = html.xpath(
            '//div[@class="page page-detail"]//td[contains(text(), "初审公告期号")]/following-sibling::td[1]//text()')  # 初审公告期号
        announcement_issue = "".join(announcement_issue)
        data["announcementIssue"] = announcement_issue.replace("\n", "").strip()

        announcement_date = html.xpath(
            '//div[@class="page page-detail"]//td[contains(text(), "初审公告日期")]/following-sibling::td[1]//text()')  # 初审公告日期
        announcement_date = "".join(announcement_date)
        data["announcementDate"] = announcement_date.replace("\n", "").strip()

        reg_issue = html.xpath(
            '//div[@class="page page-detail"]//td[contains(text(), "注册公告期号")]/following-sibling::td[1]//text()')  # 注册公告期号
        reg_issue = "".join(reg_issue)
        data["regIssue"] = reg_issue.replace("\n", "").strip()

        reg_date = html.xpath(
            '//div[@class="page page-detail"]//td[contains(text(), "注册公告日期")]/following-sibling::td[1]//text()')  # 注册公告日期
        reg_date = "".join(reg_date)
        data["regDate"] = reg_date.replace("\n", "").strip()

        is_share = html.xpath(
            '//div[@class="page page-detail"]//td[contains(text(), "是否共有商标")]/following-sibling::td[1]//text()')  # 是否共有商标
        is_share = "".join(is_share)
        data["isShare"] = 1 if "是" in is_share else 0

        private_date = html.xpath(
            '//div[@class="page page-detail"]//td[contains(text(), "专用权期限")]/following-sibling::td[1]//text()')  # 专用权期限
        private_date = "".join(private_date).replace("\n", "").strip()
        data["privateDateStart"] = private_date.split(
            "至")[0].strip() if private_date else ""  # TODO 需要修改格式
        data["privateDateEnd"] = private_date.split(
            "至")[1].strip() if private_date else ""

        shangbiaoxingshi = html.xpath(
            '//div[@class="page page-detail"]//td[contains(text(), "商标形式")]/following-sibling::td[1]//text()')  # 商标形式
        data["shangbiaoxingshi"] = "".join(
            shangbiaoxingshi).replace("\n", "").strip()

        international_reg_date = html.xpath(
            '//div[@class="page page-detail"]//td[contains(text(), "国际注册日期")]/following-sibling::td[1]//text()')  # 国际注册日期
        data["internationalRegDate"] = "".join(
            international_reg_date).replace("\n", "").strip()

        late_specified_date = html.xpath(
            '//div[@class="page page-detail"]//td[contains(text(), "后期指定日期")]/following-sibling::td[1]//text()')  # 后期指定日期
        data["lateSpecifiedDate"] = "".join(
            late_specified_date).replace("\n", "").strip()

        priority_date = html.xpath(
            '//div[@class="page page-detail"]//td[contains(text(), "优先权日期")]/following-sibling::td[1]//text()')  # 优先权日期
        data["priorityDate"] = "".join(priority_date).replace("\n", "").strip()

        agent = html.xpath(
            '//div[@class="page page-detail"]//td[contains(text(), "代理人名称")]/following-sibling::td[1]//text()')  # 代理机构/代理人名称
        data["agent"] = "".join(agent).replace("\n", "").strip()

        data["color"] = ""

        status = html.xpath(
            '//div[@class="page page-detail"]//td[contains(text(), "法律状态")]/following-sibling::td[1]//text()')  # 代理机构/代理人名称
        data["status1"] = "".join(status).replace("\n", "").strip()

        # 服务项目
        serviceNames = []
        serviceList = []
        serviceCodes = []
        service_lis = html.xpath(
            '//div[@class="page page-detail"]//td[contains(text(), "商品/服务项目")]/following-sibling::td[1]/ul/li')
        if service_lis:
            for li in service_lis:
                text = li.xpath("./text()")
                text = "".join(text).replace(" ", "_")
                text = re.sub("_+", "_", text)
                serviceList.append("_".join(text.split("_")[::-1]))
                serviceCodes.append(text.split("_")[0])
                serviceNames.append(text.split("_")[1])
        data["serviceCodes"] = serviceCodes
        data["serviceNames"] = serviceNames
        data["serviceList"] = serviceList

        # 商标流程
        flows = []
        flow_lis = html.xpath(
            '//div[@class="page page-detail"]//td[contains(text(), "商标状态")]/following-sibling::td[1]/ul/li')
        if flow_lis:
            for flow in flow_lis:
                text = flow.xpath("./text()")
                text = "".join(text).replace(" ", "_").replace("\n", "").strip()
                text = re.sub("_+", "_", text)
                flows.append({
                    "brandId": str(self.brand_id) + "_" + str(self.category),
                    "flowDate": text.split("_")[0],
                    "statusName": text.split("_")[1]
                })
        data["brandFlows"] = flows

        return data

    def get_detail_id(self):
        search_data = deepcopy(base_search_data)
        search_data["key"] = self.brand_id
        # print(search_data)
        results = self.post_info(search_url, search_data)
        # logger.info(results)
        if not results:
            return None
        for result in results:
            detail_id = result.get("id")
            category = result.get("typeCode")
            if str(category) == self.category:
                return detail_id
        else:
            return None

    def insert_data(self, data):
        try:
            self.db.insert(data)
        except Exception as e:
            logger.debug(e)

    def run_one(self):
        detail_id = self.get_detail_id()
        logger.info(f"detail_id {detail_id} branch_id {self.brand_id}")
        if not detail_id:
            self.redis_client.sadd(
                REDISKEY, self.brand_id + "_" + self.category)
            return
        detail_url = base_detail_url.format(detail_id)
        detail_response = self.get_info(detail_url, flag=self.brand_id)

        data = self.extract_data(detail_response)
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data["insertTime"] = now
        print(data)
        self.insert_data(data)
        logger.info(f"get one data ^--^  branch id : {self.brand_id}")
        pass

    def reinit(self):
        branch_ca = self.redis_client.spop(REDISKEY)
        branch_ca = branch_ca.decode()
        print("????", branch_ca)
        self.brand_id = branch_ca.split("_")[0]
        self.category = branch_ca.split("_")[-1]

    def run(self):
        while True:
            self.reinit()
            self.run_one()


if __name__ == '__main__':
    logger.info("start !!")
    num = 0
    while 1:
        a = QanDaShi()
        a.run()
