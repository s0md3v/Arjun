import re
import json
import time
import random
import requests
import warnings

import core.config as mem

warnings.filterwarnings('ignore') # Disable SSL related warnings

def requester(request, payload={}):
    if 'include' in request and request['include']:
        payload.update(request['include'])
    if mem.var['stable']:
        mem.var['delay'] = random.choice(range(6, 12))
    time.sleep(mem.var['delay'])
    url = request['url']
    if 'Host' not in request['headers']:
        this_host = re.search(r'https?://([^/]+)', url).group(1)
        request['headers']['Host'] = this_host.split('@')[1] if '@' in this_host else this_host
    if mem.var['kill']:
        return 'killed'
    try:
        if request['method'] == 'GET':
            response = requests.get(url, params=payload, headers=request['headers'], verify=False, timeout=mem.var['timeout'])
        elif request['method'] == 'JSON':
            response = requests.post(url, json=json.dumps(payload), headers=request['headers'], verify=False, timeout=mem.var['timeout'])
        else:
            response = requests.post(url, data=payload, headers=request['headers'], verify=False, timeout=mem.var['timeout'])
        return response
    except Exception as e:
        return str(e)
