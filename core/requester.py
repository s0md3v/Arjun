import re
import json
import time
import random
import warnings
import requests

import core.config

warnings.filterwarnings('ignore') # Disable SSL related warnings

def requester(url, data, headers, GET, delay, proxy):
    if core.config.globalVariables['jsonData']:
        data = json.dumps(data)
    if core.config.globalVariables['stable']:
        delay = random.choice(range(6, 12))
    time.sleep(delay)
    headers['Host'] = re.search(r'https?://([^/]+)', url).group(1)

    if proxy is not None:
        proxy={"http": proxy, "https": proxy}

    if GET:
        response = requests.get(url, params=data, headers=headers, verify=False, proxies=proxy)
    elif core.config.globalVariables['jsonData']:
        response = requests.post(url, json=data, headers=headers, verify=False, proxies=proxy)
    else:
        response = requests.post(url, data=data, headers=headers, verify=False, proxies=proxy)
    return response
