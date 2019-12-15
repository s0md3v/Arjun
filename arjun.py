#!/usr/bin/env python3

from __future__ import print_function

from core.colors import green, white, end, info, bad, good, run

print('''%s    _
   /_| _ '
  (  |/ /(//) v1.6
      _/      %s
''' % (green, end))

try:
    import concurrent.futures
except ImportError:
    print('%s Please use Python > 3.2 to run Arjun.' % bad)
    quit()

import re
import json
import time
import argparse

import core.config
from core.prompt import prompt
from core.requester import requester
from core.utils import e, d, stabilize, randomString, slicer, joiner, unityExtracter, getParams, removeTags, extractHeaders

parser = argparse.ArgumentParser() # defines the parser
# Arguments that can be supplied
parser.add_argument('-u', help='target url', dest='url')
parser.add_argument('-o', help='path for the output file', dest='output_file')
parser.add_argument('-d', help='request delay', dest='delay', type=float, default=0)
parser.add_argument('-t', help='number of threads', dest='threads', type=int, default=2)
parser.add_argument('-f', help='wordlist path', dest='wordlist', default='./db/params.txt')
parser.add_argument('--urls', help='file containing target urls', dest='url_file')
parser.add_argument('--get', help='use get method', dest='GET', action='store_true')
parser.add_argument('--post', help='use post method', dest='POST', action='store_true')
parser.add_argument('--headers', help='add headers', dest='headers', nargs='?', const=True)
parser.add_argument('--json', help='treat post data as json', dest='jsonData', action='store_true')
parser.add_argument('--stable', help='prefer stability over speed', dest='stable', action='store_true')
parser.add_argument('--include', help='include this data in every request', dest='include', default={})
args = parser.parse_args() # arguments to be parsed

url = args.url
delay = args.delay
stable = args.stable
include = args.include
headers = args.headers
jsonData = args.jsonData
url_file = args.url_file
wordlist = args.wordlist
threadCount = args.threads

if stable or delay:
    threadCount = 1

core.config.globalVariables = vars(args)

if type(headers) == bool:
    headers = extractHeaders(prompt())
elif type(headers) == str:
    headers = extractHeaders(headers)
else:
    headers = {'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0',
                'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language' : 'en-US,en;q=0.5',
                'Accept-Encoding' : 'gzip, deflate',
                'Connection' : 'keep-alive',
                'Upgrade-Insecure-Requests' : '1'}

if jsonData:
    headers['Content-type'] = 'application/json'

if not (args.GET or args.POST or args.jsonData) or args.GET:
    GET = True
else:
    GET = False

include = getParams(include)

paramList = []
try:
    with open(wordlist, 'r', encoding="utf8") as file:
        for line in file:
            paramList.append(line.strip('\n'))
except FileNotFoundError:
    print('%s The specified file for parameters doesn\'t exist' % bad)
    quit()

urls = []

if url_file:
    try:
        with open(url_file, 'r', encoding="utf8") as file:
            for line in file:
                urls.append(line.strip('\n'))
    except FileNotFoundError:
        print('%s The specified file for URLs doesn\'t exist' % bad)
        quit()

if not url and not url_file:
    print('%s No URL specified.' % bad)
    quit()

def heuristic(response, paramList):
    done = []
    forms = re.findall(r'(?i)(?s)<form.*?</form.*?>', response)
    for form in forms:
        method = re.search(r'(?i)method=[\'"](.*?)[\'"]', form)
        inputs = re.findall(r'(?i)(?s)<input.*?>', response)
        if inputs != None and method != None:
            for inp in inputs:
                inpName = re.search(r'(?i)name=[\'"](.*?)[\'"]', inp)
                if inpName:
                    inpName = d(e(inpName.group(1)))
                    if inpName not in done:
                        if inpName in paramList:
                            paramList.remove(inpName)
                        done.append(inpName)
                        paramList.insert(0, inpName)
                        print('%s Heuristic found a potential %s parameter: %s%s%s' % (good, method.group(1), green, inpName, end))
                        print('%s Prioritizing it' % info)
    emptyJSvars = re.finditer(r'var\s+([^=]+)\s*=\s*[\'"`][\'"`]', response)
    for each in emptyJSvars:
        inpName = each.group(1)
        done.append(inpName)
        paramList.insert(0, inpName)
        print('%s Heuristic found a potential parameter: %s%s%s' % (good, green, inpName, end))
        print('%s Prioritizing it' % info)

def quickBruter(params, originalResponse, originalCode, reflections, factors, include, delay, headers, url, GET):
    joined = joiner(params, include)
    newResponse = requester(url, joined, headers, GET, delay)
    if newResponse.status_code == 429:
        if core.config.globalVariables['stable']:
            print('%s Hit rate limit, stabilizing the connection..')
            time.sleep(30)
            return params
        else:
            print('%s Target has rate limiting in place, please use --stable switch' % bad)
            raise ConnectionError
    if newResponse.status_code != originalCode:
        return params
    elif factors['sameHTML'] and len(newResponse.text) != (len(originalResponse)):
        return params
    elif factors['samePlainText'] and len(removeTags(originalResponse)) != len(removeTags(newResponse.text)):
        return params
    elif True:
        for param, value in joined.items():
            if param not in include and newResponse.text.count(value) != reflections:
                return params
    else:
        return False

def narrower(oldParamList, url, include, headers, GET, delay, originalResponse, originalCode, reflections, factors, threadCount):
    newParamList = []
    threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=threadCount)
    futures = (threadpool.submit(quickBruter, part, originalResponse, originalCode, reflections, factors, include, delay, headers, url, GET) for part in oldParamList)
    for i, result in enumerate(concurrent.futures.as_completed(futures)):
        if result.result():
            newParamList.extend(slicer(result.result()))
        print('%s Processing: %i/%-6i' % (info, i + 1, len(oldParamList)), end='\r')
    return newParamList

def initialize(url, include, headers, GET, delay, paramList, threadCount):
    url = stabilize(url)
    if not url:
        return {}
    else:
        print('%s Analysing the content of the webpage' % run)
        firstResponse = requester(url, include, headers, GET, delay)

        print('%s Analysing behaviour for a non-existent parameter' % run)

        originalFuzz = randomString(6)
        data = {originalFuzz : originalFuzz[::-1]}
        data.update(include)
        response = requester(url, data, headers, GET, delay)
        reflections = response.text.count(originalFuzz[::-1])
        print('%s Reflections: %s%i%s' % (info, green, reflections, end))

        originalResponse = response.text
        originalCode = response.status_code
        print('%s Response Code: %s%i%s' % (info, green, originalCode, end))

        newLength = len(response.text)
        plainText = removeTags(originalResponse)
        plainTextLength = len(plainText)
        print('%s Content Length: %s%i%s' % (info, green, newLength, end))
        print('%s Plain-text Length: %s%i%s' % (info, green, plainTextLength, end))

        factors = {'sameHTML': False, 'samePlainText': False}
        if len(firstResponse.text) == len(originalResponse):
            factors['sameHTML'] = True
        elif len(removeTags(firstResponse.text)) == len(plainText):
            factors['samePlainText'] = True

        print('%s Parsing webpage for potential parameters' % run)
        heuristic(firstResponse.text, paramList)

        fuzz = randomString(8)
        data = {fuzz : fuzz[::-1]}
        data.update(include)

        print('%s Performing heuristic level checks' % run)

        toBeChecked = slicer(paramList, 50)
        foundParamsTemp = []
        while True:
            toBeChecked = narrower(toBeChecked, url, include, headers, GET, delay, originalResponse, originalCode, reflections, factors, threadCount)
            toBeChecked = unityExtracter(toBeChecked, foundParamsTemp)
            if not toBeChecked:
                break

        foundParams = []

        for param in foundParamsTemp:
            exists = quickBruter([param], originalResponse, originalCode, reflections, factors, include, delay, headers, url, GET)
            if exists:
                foundParams.append(param)

        print('%s Scan Completed    ' % info)

        for each in foundParams:
            print('%s Valid parameter found: %s%s%s' % (good, green, each, end))
        if not foundParams:
            print('%s Unable to verify existence of parameters detected by heuristic.' % bad)
        return foundParams

finalResult = {}

try:
    if url:
        finalResult[url] = []
        try:
            finalResult[url] = initialize(url, include, headers, GET, delay, paramList, threadCount)
        except ConnectionError:
            print('%s Target has rate limiting in place, please use --stable switch.' % bad)
            quit()
    elif urls:
        for url in urls:
            finalResult[url] = []
            print('%s Scanning: %s' % (run, url))
            try:
                finalResult[url] = initialize(url, include, headers, GET, delay, list(paramList), threadCount)
                if finalResult[url]:
                    print('%s Parameters found: %s' % (good, ', '.join(finalResult[url])))
            except ConnectionError:
                print('%s Target has rate limiting in place, please use --stable switch.' % bad)
                pass
except KeyboardInterrupt:
    print('%s Exiting..                ' % bad)
    quit()

# Finally, export to json
if args.output_file and finalResult:
    print('%s Saving output to JSON file in %s' % (info, args.output_file))
    with open(str(args.output_file), 'w+', encoding="utf8") as json_output:
        json.dump(finalResult, json_output, sort_keys=True, indent=4)
