import ssl
import time
import requests
from typing import Union
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from google_play_scraper.exceptions import ExtraHTTPError, NotFoundError

ssl._create_default_https_context = ssl._create_unverified_context

MAX_RETRIES = 3
RATE_LIMIT_DELAY = 5

def _urlopen(url, proxy = None):
    resp = ""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    try:
        if proxy:
            response = requests.get(url, proxies=proxy, headers=headers)
        else:
            response = requests.get(url, headers=headers)
        print(response.status_code)
        if response.status_code == 200:
            resp = response.text 
        else:
            print(f"Request failed with status code: {response.status_code}")

    # except requests.exceptions.SSLError as e:
    #     # Handling SSLError exception
    #     print(f"SSL Error occurred: {e}")
    #     return _urlopen(url, proxy)  
    # except requests.exceptions.ProxyError as e:
    #     # Handling ProxyError exception
    #     print(f"Proxy Error occurred: {e}")
    #     return _urlopen(url, proxy)  
    except HTTPError as e:
        if e.code == 404:
            raise NotFoundError("App not found(404).")
        else:
            raise ExtraHTTPError(
                "App not found. Status code {} returned.".format(e.code)
            )
    return resp


def post(url: str, data: Union[str, bytes], headers: dict) -> str:
    last_exception = None
    rate_exceeded_count = 0
    for _ in range(MAX_RETRIES):
        try:
            resp = _urlopen(Request(url, data=data, headers=headers))
        except Exception as e:
            last_exception = e
            continue
        if "com.google.play.gateway.proto.PlayGatewayError" in resp:
            rate_exceeded_count += 1
            last_exception = Exception("com.google.play.gateway.proto.PlayGatewayError")
            time.sleep(RATE_LIMIT_DELAY * rate_exceeded_count)
            continue
        return resp
    raise last_exception


def get(url: str, proxy = None) -> str:
    return _urlopen(url, proxy)
