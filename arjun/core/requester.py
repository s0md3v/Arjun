"""Handle the requests."""
import random
import time
import warnings

import requests

warnings.filterwarnings("ignore")  # Disable SSL related warnings

USER_AGENTS = [
    "Mozilla/5.0 (X11; Linux i686; rv:60.0) Gecko/20100101 Firefox/60.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
    " like Gecko) Chrome/60.0.3112.113 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, "
    "like Gecko) Chrome/56.0.2924.87 Safari/537.36 OPR/43.0.2442.991",
]


def requester(url, data, headers, get, delay):
    """Handle the requests."""
    time.sleep(delay)

    if headers:
        if "User-Agent" not in headers:
            headers["User-Agent"] = random.choice(USER_AGENTS)
    if get:
        response = requests.get(
            url, params=data, headers=headers, verify=False, timeout=10
        )
    else:
        response = requests.post(
            url, data=data, headers=headers, verify=False, timeout=10
        )

    return response
