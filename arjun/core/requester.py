import json
import time
import random
import requests
import warnings

import arjun.core.config as mem

from arjun.core.utils import dict_to_xml

warnings.filterwarnings('ignore') # Disable SSL related warnings

def requester(request, payload={}):
    """
    central function for making http requests
    returns str on error otherwise response object of requests library
    """
    if 'include' in request and request['include']:
        payload.update(request['include'])
    if mem.var['stable']:
        mem.var['delay'] = random.choice(range(6, 12))
    time.sleep(mem.var['delay'])
    url = request['url']
    if mem.var['kill']:
        return 'killed'
    if mem.var['proxy']: proxies = {'http': 'http://'+mem.var['proxy'], 'https': 'https://'+mem.var['proxy']}
    try:
        if request['method'] == 'GET':
            response = requests.get(url,
                params=payload,
                headers=request['headers'],
                verify=False,
                allow_redirects=False,
                timeout=mem.var['timeout'],
                proxies=proxies,
            )
        elif request['method'] == 'JSON':
            request['headers']['Content-Type'] = 'application/json'
            if mem.var['include'] and '$arjun$' in mem.var['include']:
                payload = mem.var['include'].replace('$arjun$',
                    json.dumps(payload).rstrip('}').lstrip('{'))
                response = requests.post(url,
                    data=payload,
                    headers=request['headers'],
                    verify=False,
                    allow_redirects=False,
                    timeout=mem.var['timeout'],
                    proxies=proxies,
                )
            else:
                response = requests.post(url,
                    json=payload,
                    headers=request['headers'],
                    verify=False,
                    allow_redirects=False,
                    timeout=mem.var['timeout'],
                    proxies=proxies,
                )
        elif request['method'] == 'XML':
            request['headers']['Content-Type'] = 'application/xml'
            payload = mem.var['include'].replace('$arjun$',
                dict_to_xml(payload))
            response = requests.post(url,
                data=payload,
                headers=request['headers'],
                verify=False,
                allow_redirects=False,
                timeout=mem.var['timeout'],
                proxies=proxies,
            )
        else:
            response = requests.post(url,
                data=payload,
                headers=request['headers'],
                verify=False,
                allow_redirects=False,
                timeout=mem.var['timeout'],
                proxies=proxies,
            )
        return response
    except Exception as e:
        return str(e)
