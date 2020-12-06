import re
from core.utils import reader, parse_request

burp_regex = re.compile(r'''(?m)^    <url><!\[CDATA\[(.+?)\]\]></url>
    <host ip="[^"]*">[^<]+</host>
    <port>[^<]*</port>
    <protocol>[^<]*</protocol>
    <method><!\[CDATA\[(.+?)\]\]></method>
    <path>.*</path>
    <extension>(.*)</extension>
    <request base64="(?:false|true)"><!\[CDATA\[([\s\S]+?)]]></request>
    <status>([^<]*)</status>
    <responselength>([^<]*)</responselength>
    <mimetype>([^<]*)</mimetype>''')


def burp_import(path):
	requests = []
	content = reader(path)
	matches = re.finditer(burp_regex, content)
	for match in matches:
		request = parse_request(match.group(4))
		headers = request['headers']
		if match.group(7) in ('HTML', 'JSON'):
			requests.append({
				'url': match.group(1),
				'method': match.group(2),
				'extension': match.group(3),
				'headers': headers,
				'include': request['data'],
				'code': match.group(5),
				'length': match.group(6),
				'mime': match.group(7)
			})
	return requests


def urls_import(path, method, headers, include):
	requests = []
	urls = reader(path, mode='lines')
	for url in urls:
		requests.append({
			'url': url,
			'method': method,
			'headers': headers,
			'data': include
		})
	return requests


def request_import(path):
	return parse_request(reader(path))


def importer(path, method, headers, include):
    with open(path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.startswith('<?xml'):
                return burp_import(path)
            elif line.startswith(('http://', 'https://')):
                return urls_import(path, method, headers, include)
            elif line.startswith(('GET', 'POST')):
                return request_import(path)
            return 'unknown'
