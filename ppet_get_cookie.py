import asyncio
import time
import random
from pyppeteer import launch
import pyppeteer
import requests_async as requests
import aioredis
from get_ip import get_ip_from_url
from redis_api import connection
from conf import COOKIEKEY, REDISPORT, REDISHOST, REDISPASSWORD
import json

from logging import getLogger
import logging

pyppeteer_level = logging.WARNING
logging.getLogger('websockets.protocol').setLevel(pyppeteer_level)
logging.getLogger('pyppeteer').setLevel(pyppeteer_level)

first_url = "https://so.quandashi.com/index/search?key=%E5%B0%8F%E7%B1%B3"


class Cookei(object):

    def __init__(self):
        self.cookie = None

    async def get_proxies(self):
        self.ip = get_ip_from_url()
        self.proxies = {
            "http": f"http://{self.ip}",
            "https": f"https://{self.ip}"
        }

    async def start_ppet(self):
        self.browser = await launch(
            {"headless": False, 'dumpio': True, "userDataDir": "./userData", 'args': [
                f'--proxy-server={self.ip}', '-no-sandbox']}
        )
        # ====================== headless ===============================
        # self.browser = await launch(
        #     {"headless": True, 'dumpio': True, "userDataDir": "./userData", 'args': [
        #         f'--proxy-server={self.ip}', '-no-sandbox']}
        # )
        print("started browser!")

    async def get_cookie(self):
        while 1:
            try:
                page = await self.browser.newPage()
                await page.setViewport(viewport={'width': 1920, 'height': 1080})
                await page.setJavaScriptEnabled(enabled=True)

                # 设置navigator属性，防止检测出driver控制
                await page.evaluateOnNewDocument('() =>{ Object.defineProperties(navigator,'
                                                 '{ webdriver:{ get: () => false } }) }')
                # 访问搜索页
                await page.goto(first_url, timeout=30000)

                await asyncio.sleep(1)

                click_but = await page.xpath(
                    '//a[@class="button btn-search"]')
                time.sleep(1)

                # 模拟操作鼠标
                # 点击搜索

                for i in range(3):
                    print("random move mouse!")
                    xff = random.choice(range(1000))
                    yff = random.choice(range(500))
                    await page.mouse.down()
                    await page.mouse.move(xff, yff)
                    await page.mouse.up()
                    await asyncio.sleep(1)
                # time.sleep(444)
                size = await click_but[0].boundingBox()
                print("start move mouse!!")
                await page.mouse.move(float(size.get("x")) + float(size.get("width")) / 2, float(size.get("y")) + float(size.get("height")) / 2, {'delay': random.randint(1000, 2000)})

                await page.mouse.down()
                await page.mouse.up()
                print("end !!!")

                # ==============================================
                await page.waitForNavigation()
                # await asyncio.sleep(5)
                result_list = await page.xpath(
                    "//ul[@class='search-list']")
                if not result_list:
                    print("结果没加载出来！！！")
                if await page.xpath(
                        '//div[@class="geetest_widget"]'):
                    print("需要点字验证！！！！！！")

                # ===================================================
                #
                # await page.goto(first_url, timeout=30000)
                # time.sleep(12)
                cookie = "PHPSESSID="
                # cookie = ""
                for i in await page.cookies():
                    if i["name"] == "PHPSESSID":
                        cookie += i.get("value", "")
                print(cookie)
                self.cookie = cookie
                await page.close()
                await self.browser.close()
                return
            except Exception as e:
                print("error :", e)
                try:
                    await page.close()
                    await self.browser.close()
                except Exception as e:
                    print(e)
                    pass
                await self.get_proxies()
                await self.start_ppet()

    async def cookie_to_redis(self):
        conn = await aioredis.create_connection(
            (REDISHOST, REDISPORT), password=REDISPASSWORD, db=0)
        now_stamp = time.time()
        val = await conn.execute("sadd", COOKIEKEY, json.dumps({"cookie": self.cookie, "ip": self.ip, "timestamp": now_stamp}))
        conn.close()
        await conn.wait_closed()
        return val

    async def pop_cookie(self):
        cookie = await self.redis_client.execute("spop", COOKIEKEY)
        await self.redis_client.get()
        return cookie
        pass

    async def run_one(self):
        while 1:
            await self.get_proxies()
            await self.start_ppet()
            await self.get_cookie()
            await self.cookie_to_redis()
        pass

    def run(self):
        tasks = []
        for i in range(1):
            tasks.append(asyncio.ensure_future(self.run_one()))
        asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))


if __name__ == '__main__':
    a = Cookei()
    a.run()
