import re
import string
import random
import requests
from core.colors import bad

def slicer(array, n=2):
    k, m = divmod(len(array), n)
    return (array[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))

def joiner(array):
    params = {}
    for element in array:
        params[element] = randomString(6)
    return params

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
            pass
        else:
            print ('%s Unable to connect to the target.' % bad)
            quit()
    return url

def removeTags(html):
    return re.sub(r'(?s)<.*?>', '', html)

def lineComparer(response1, response2):
    response1 = response1.split('\n')
    response2 = response2.split('\n')
    num = 0
    dynamicLines = []
    for line1, line2 in zip(response1, response2):
        if line1 != line2:
            dynamicLines.append(num)
        num += 1
    return dynamicLines

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
