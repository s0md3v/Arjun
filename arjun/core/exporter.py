import json
import requests

from urllib.parse import urlparse, urlencode

import arjun.core.config as mem
from arjun.core.utils import populate, dict_to_xml

from arjun.core.utils import create_query_string


def json_export(result):
    """
    exports result to a file in JSON format
    """
    with open(mem.var['json_file'], 'w+', encoding='utf8') as json_output:
        json.dump(result, json_output, sort_keys=True, indent=4)


def burp_export(result):
    """
    exports results to Burp Suite by sending request to Burp proxy
    """
    proxy = ('' if ':' in mem.var['burp_proxy'] else '127.0.0.1:') + mem.var['burp_proxy']
    proxies = {
        'http': 'http://' + proxy,
        'https': 'https://' + proxy
    }
    for url, data in result.items():
        if data['method'] == 'GET':
            requests.get(url, params=populate(data['params']), headers=data['headers'], proxies=proxies, verify=False)
        elif data['method'] == 'POST':
            requests.post(url, data=populate(data['params']), headers=data['headers'], proxies=proxies, verify=False)
        elif data['method'] == 'JSON':
            requests.post(url, json=populate(data['params']), headers=data['headers'], proxies=proxies, verify=False)


def text_export(result):
    """
    exports results to a text file, one url per line
    """
    with open(mem.var['text_file'], 'a+', encoding='utf8') as text_file:
        for url, data in result.items():
            clean_url = url.lstrip('/')
            if data['method'] == 'JSON':
                text_file.write(clean_url + '\t' + json.dumps(populate(data['params'])) + '\n')
            else:
                query_string = create_query_string(data['params'])
                if '?' in clean_url:
                    query_string = query_string.replace('?', '&', 1)
                if data['method'] == 'GET':
                    text_file.write(clean_url + query_string + '\n')
                elif data['method'] == 'POST':
                    text_file.write(clean_url + '\t' + query_string + '\n')


def build_raw_request(url, data):
    """
    builds a raw HTTP request string for a single result
    returns str
    """
    parsed = urlparse(url)
    host = parsed.netloc
    path = parsed.path or '/'
    method = data['method']
    verb = 'GET' if method == 'GET' else 'POST'
    headers = {k: v for k, v in data['headers'].items() if k.lower() not in ('content-type', 'content-length')}
    params = populate(data['params'])

    body = ''
    if method == 'GET':
        query = urlencode(params)
        merged = '&'.join(part for part in (parsed.query, query) if part)
        target = path + ('?' + merged if merged else '')
    else:
        target = path
        if method == 'JSON':
            body = json.dumps(params)
            headers['Content-Type'] = 'application/json'
        elif method == 'XML':
            body = dict_to_xml(params)
            headers['Content-Type'] = 'application/xml'
        else:
            body = urlencode(params)
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
        headers['Content-Length'] = str(len(body))

    lines = ['%s %s HTTP/1.1' % (verb, target)]
    if host and not any(name.lower() == 'host' for name in headers):
        lines.append('Host: ' + host)
    for name, value in headers.items():
        lines.append('%s: %s' % (name, value))
    return '\r\n'.join(lines) + '\r\n\r\n' + body


def raw_export(result):
    """
    exports results as raw HTTP requests so they can be loaded into other tools
    """
    with open(mem.var['raw_file'], 'a+', encoding='utf8') as raw_file:
        for url, data in result.items():
            raw_file.write(build_raw_request(url, data) + '\n\n')


def exporter(result):
    """
    main exporter function that calls other export functions
    """
    if mem.var['json_file']:
        json_export(result)
    if mem.var['text_file']:
        text_export(result)
    if mem.var['raw_file']:
        raw_export(result)
    if mem.var['burp_proxy']:
        burp_export(result)
