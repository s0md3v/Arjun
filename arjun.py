#!/usr/bin/env python
import requests
import sys
import argparse
import re
import threading
lock = threading.Lock()

# Just some colors and shit
white = '\033[1;97m'
green = '\033[1;32m'
red = '\033[1;31m'
yellow = '\033[1;33m'
end = '\033[1;m'
info = '\033[1;33m[!]\033[1;m'
que =  '\033[1;34m[?]\033[1;m'
bad = '\033[1;31m[-]\033[1;m'
good = '\033[1;32m[+]\033[1;m'
run = '\033[1;97m[~]\033[1;m'

print ("""%s    _         
   /_| _ '    
  (  |/ /(//) %s(v0.8 beta)%s
      _/      %s""" % (green, white, green, end))

if sys.version_info < (3, 0):
    input = raw_input

parser = argparse.ArgumentParser() #defines the parser
#Arguements that can be supplied
parser.add_argument("-u", help="target url", dest='url')
parser.add_argument("--get", help="use get method", dest='GET', action="store_true")
parser.add_argument("--post", help="use post method", dest='POST', action="store_true")
parser.add_argument("--threads", help="number of threads", dest='n', type=int)
args = parser.parse_args() #arguments to be parsed

url = args.url
if args.n:
    n = args.n
else:
    n = 2

if args.GET:
    GET, POST = True, False
if args.POST:
    GET, POST = False, True

fuzz = 'd3v3v'

params = []
with open('params.txt', 'r') as param_list:
    for param in param_list:
        params.append(param.strip('\n'))


def make_request(url, param, GET, POST):
    injected = {param : fuzz}
    if GET:
        return requests.get(url, params=injected)
    elif POST:
        return requests.post(url, data=injected)


def main(url, GET, POST, o_reflection, o_http_code, o_headers):
    progress = 0
    for param in params:
        lock.acquire()
        sys.stdout.write('\r%s Parameters Scanned: %i/%i' % (run, progress, len(params)))
        sys.stdout.flush()
        response = make_request(url, param, GET, POST)
        content = response.text.replace('?%s=' % param, '')
        if '\'%s\'' % fuzz in content or '"%s"' % fuzz in content or ' %s ' % fuzz in content:
            content_length = len(content) - content.count(fuzz) * len(fuzz)
            reflection = True
        else:
            reflection = False
            content_length = len(content)
        http_code = response.status_code
        headers = str(response.headers).count('\':')
        reasons = []
        if http_code != o_http_code:
            reasons.append('%s Different HTTP response code recieved.' % info)
        if reflection != o_reflection:
            if reflection:
                reasons.append('%s Parameter\'s value was reflected in webpage' % info)
        if headers != o_headers:
            reasons.append('%s Different HTTP headers recieved.' % info)
        if len(reasons) != 0:
            print ('\n%s I believe %s is a valid parameter due to following reason(s):' % (good, param))
            for reason in reasons:
                print (reason)
        progress += 1
        lock.release()
    print ('%s\n Scan completed!' % info)

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

url = stabilize(url)

print ('%s Lets see how target deals with a non-existent parameter' % run)
response = make_request(url, '83bxAm', GET, POST)
o_content = response.text.replace('?%s=' % '83bxAm', '')
matches = re.findall(r'<input[^<]*name=\'[^<]*\'*>|<input[^<]*name="[^<]*"*>', o_content)
for match in matches:
    found_param = match.encode('utf-8').split('name=')[1].split(' ')[0].replace('\'', '').replace('"', '')
    print ('%s Heuristics found a potentially valid parameter: %s%s%s. Priortizing it.' % (good, green, found_param, end))
    params.insert(0, found_param)
if '\'%s\'' % fuzz in o_content or '"%s"' % fuzz in o_content or ' %s ' % fuzz in o_content:
    o_count = o_content.count(fuzz)
    print ('%s Parameter\'s value got reflected %i time(s) in webpage.' % (info, o_count))
    o_reflection = True
else:
    print ('%s Parameter\'s value didn\'t get reflected in webpage.' % info)
    o_reflection = False
o_http_code = response.status_code
print ('%s HTTP Response Code: %i' % (info, o_http_code))
o_headers = str(response.headers).count('\':')
print ('%s Number of HTTP Response Headers: %i' % (info, o_headers))

threads = []

for i in range(1, n):
    task = threading.Thread(target=main, args=(url, GET, POST, o_reflection, o_http_code, o_headers,))
    threads.append(task)

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()
