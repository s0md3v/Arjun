import requests
import requests
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from lxml import html

def wayback(host, page):
    payload = {
        'url': host,
        'matchType': 'host',
        'collapse': 'urlkey',
        'fl': 'original',
        'page': page,
        'limit': 10000
    }
    headers = {
        'User-Agent': 'Mozilla'
    }
    these_params = set()
    try:
        with requests.Session() as session:
            with ThreadPoolExecutor() as executor:
                def fetch_url(url):
                    return session.get(url, params=payload, headers=headers, verify=False)
                results = [executor.submit(fetch_url, 'http://web.archive.org/cdx/search?filter=mimetype:text/html&filter=statuscode:200') for _ in range(10000)]
                for result in results:
                    response = result.result().text
                    if not response:
                        return (these_params, False, 'wayback')
                    doc = html.fromstring(response)
                    for url in doc.xpath('//a/@href'):
                        for param in urlparse(url).query.split('&'):
                            these_params.add(param.split('=')[0])
                return (these_params, True, 'wayback')
    except requests.exceptions.ConnectionError:
        return (these_params, False, 'wayback')
