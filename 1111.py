import requests

s = """Accept: application/json, text/javascript, */*; q=0.01
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
Connection: keep-alive
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
Cookie: PHPSESSID=r07ie32t5sbom5eensd37t0vj7
Host: so.quandashi.com
User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3494.0 Safari/537.36
"""


def format_s(s):
    return {item.split(':', 1)[0].strip(): item.split(':', 1)[1].strip() for item in s.split('\n') if item}


bease_headers = format_s(s)

from conf import base_search_data, search_url
from get_ip import get_ip_from_url

ip = get_ip_from_url()
proxies = {
    "http": f"http://{ip}",
            "https": f"https://{ip}"
}

# bease_headers["Cookie"] = "PHPSESSID=qt599i3qm50r7jp4oqqm71jvv"

while 1:
    try:
        res = requests.post(search_url, headers=bease_headers, data=base_search_data,
                            proxies=proxies, timeout=3)
        break
    except Exception as e:
        print(e)
        ip = get_ip_from_url()
        proxies = {
            "http": f"http://{ip}",
                    "https": f"https://{ip}"
        }
res.encoding = res.apparent_encoding
json_res = res.json()
print(json_res)
