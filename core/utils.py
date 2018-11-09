import string
import random
import requests
from core.colors import bad

def stabilize(url):
    if 'http' not in url:
        try:
            requests.get('http://%s' % url) # Makes request to the target with http schema
            url = 'http://%s' % url
        except: # if it fails, maybe the target uses https schema
            url = 'https://%s' % url

    try:
        requests.get(url) # Makes request to the target
    except Exception as e: # if it fails, the target is unreachable
        if 'ssl' in str(e).lower():
            print ('%s Unable to verify target\'s SSL certificate.' % bad)
            quit()
        else:
            print ('%s Unable to connect to the target.' % bad)
            quit()
    return url

def randomString(length):
   return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

def flattenParams(params):
    flatted = []
    for name, value in params.items():
        flatted.append(name + '=' + value)
    return '?' + '&'.join(flatted)

def e(string):
    return string.encode('utf-8')

def d(string):
    return string.decode('utf-8')