import re
import json
import random
import requests

import concurrent.futures
from urllib.parse import urlparse

from plugins.otx import otx
from plugins.wayback import wayback
from plugins.commoncrawl import commoncrawl

from core.colors import info

def lcs(s1, s2):
    """
    finds longest common substring between two strings
    returns str
    """
    m = [[0] * (1 + len(s2)) for i in range(1 + len(s1))]
    longest, x_longest = 0, 0
    for x in range(1, 1 + len(s1)):
        for y in range(1, 1 + len(s2)):
            if s1[x - 1] == s2[y - 1]:
                m[x][y] = m[x - 1][y - 1] + 1
                if m[x][y] > longest:
                    longest = m[x][y]
                    x_longest = x
            else:
                m[x][y] = 0
    return s1[x_longest - longest: x_longest]


def extractHeaders(headers):
    """
    parses headers provided through command line
    returns dict
    """
    headers = headers.replace('\\n', '\n')
    return parse_headers(headers)


def confirm(array_of_dicts, usable):
    """
    extracts the value from single valued dict from an array of dicts
    returns a array of dicts
    """
    param_groups = []
    for dic in array_of_dicts:
        if len(dic) == 1:
            usable.append(dic)
        else:
            param_groups.append(dic)
    return param_groups


def slicer(dic, n=2):
    """
    divides dict into n parts
    returns array containing n dicts
    """
    listed = list(dic.items())
    k, m = divmod(len(dic), n)
    return [dict(listed[i * k + min(i, m):(i + 1) * k + min(i + 1, m)]) for i in range(n)]


def populate(array):
    """
    converts a list of parameters into parameter and value pair
    returns dict
    """
    return {name: '1' * (6 - len(str(i))) + str(i) for i, name in enumerate(array)}


def stable_request(url, headers):
    """
    guarantees crash-proof HTTP(S) requests
    returns None in case of failure, returns a "response" object otherwise
    """
    parsed = urlparse(url)
    scheme, host, path = parsed.scheme, parsed.netloc, parsed.path
    schemes = (['https', 'http'] if scheme == 'https' else ['http', 'https'])
    for scheme in schemes:
        try:
            return requests.get(
                scheme + '://' + host + path,
                headers=headers,
                verify=False,
                timeout=10).status_code
        except Exception as e:
            if 'ConnectionError' not in str(e):
                continue
        return None


def removeTags(html):
    """
    removes all the html from a webpage source
    """
    return re.sub(r'(?s)<.*?>', '', html)


def lineComparer(response1, response2):
    """
    compares two webpage and finds the non-matching lines
    """
    response1 = response1.split('\n')
    response2 = response2.split('\n')
    num = 0
    dynamicLines = []
    for line1, line2 in zip(response1, response2):
        if line1 != line2:
            dynamicLines.append(num)
        num += 1
    return dynamicLines


def randomString(n):
    """
    generates a random string of length n
    """
    return ''.join(str(random.choice(range(10))) for i in range(n))


def getParams(include):
    """
    loads parameters from JSON/query string
    """
    params = {}
    if include:
        if include.startswith('{'):
            params = json.loads(str(include).replace('\'', '"'))
            return params
        else:
            cleaned = include.split('?')[-1]
            parts = cleaned.split('&')
            for part in parts:
                each = part.split('=')
                try:
                    params[each[0]] = each[1]
                except IndexError:
                    params = {}
    return params


def reader(path, mode='string'):
    """
    reads a file
    returns a string/array containing the content of the file
    """
    with open(path, 'r', encoding='utf-8') as file:
        if mode == 'lines':
            return list(filter(None, [line.rstrip('\n') for line in file]))
        else:
            return ''.join([line for line in file])


def extract_js(response):
    """
    extracts javascript from a given string
    """
    return re.findall(r'(?s)<script[^>]+>([^<].+?)</script', response.lower(), re.I)


def parse_headers(string):
    """
    parses headers
    return dict
    """
    result = {}
    for line in string.split('\n'):
        if len(line) > 1:
            splitted = line.split(':')
            result[splitted[0]] = ':'.join(splitted[1:]).strip()
    return result


def parse_request(string):
    """
    parses http request
    returns dict
    """
    result = {}
    match = re.search(r'(?:([a-zA-Z0-9]+) ([^ ]+) [^ ]+\n)?([\s\S]+\n)\n?([\s\S]+)?', string)
    result['method'] = match.group(1)
    result['path'] = match.group(2)
    result['headers'] = parse_headers(match.group(3))
    result['data'] = match.group(4)
    return result


def http_import(path):
    """
    parses http request from a file
    returns dict
    """
    return parse_request(reader(path))


def fetch_params(host):
    """
    fetch parameters from passive sources
    returns list
    """
    available_plugins = {'commoncrawl': commoncrawl, 'otx': otx, 'wayback': wayback}
    page = 0
    progress = 0
    params = {}
    while len(available_plugins) > 0 and page <= 10:
        threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=len(available_plugins))
        futures = (threadpool.submit(func, host, page) for func in available_plugins.values())
        for each in concurrent.futures.as_completed(futures):
            if progress < 98:
                progress += 3
            this_result = each.result()
            if not this_result[1]:
                progress += ((10 - page) * 10 / 3)
                del available_plugins[this_result[2]]
            if len(this_result[0]) > 1:
                if not params:
                    params = this_result[0]
                else:
                    params.update(this_result[0])
            print('%s Progress: %i%%' % (info, progress), end='\r')
        page += 1
    print('%s Progress: %i%%' % (info, 100), end='\r')
    return params
