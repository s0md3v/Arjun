#!/usr/bin/env python3

import re
import sys
import requests
import argparse
import concurrent.futures
from urllib.parse import unquote

from core.prompt import prompt
from core.requester import requester
from core.colors import red, green, white, end, info, bad, good, run
from core.utils import e, d, stabilize, flattenParams, randomString, slicer, joiner, unityExtracter

print ('''%s    _         
   /_| _ '    
  (  |/ /(//) %sv1.2-beta%s
      _/      %s''' % (green, white, green, end))


parser = argparse.ArgumentParser() #defines the parser
#Arguements that can be supplied
parser.add_argument('-u', help='target url', dest='url')
parser.add_argument('-d', help='request delay', dest='delay', type=int)
parser.add_argument('-t', help='number of threads', dest='threads', type=int)
parser.add_argument('-f', help='file path', dest='file')
parser.add_argument('--get', help='use get method', dest='GET', action='store_true')
parser.add_argument('--post', help='use post method', dest='POST', action='store_true')
parser.add_argument('--headers', help='http headers prompt', dest='headers', action='store_true')
args = parser.parse_args() #arguments to be parsed

url = args.url
file = args.file or './db/params.txt'
headers = args.headers
delay = args.delay or 0
threadCount = args.threads or 2

def extractHeaders(headers):
    sortedHeaders = {}
    matches = re.findall(r'(.*):\s(.*)', headers)
    for match in matches:
        header = match[0]
        value = match[1]
        try:
            if value[-1] == ',':
                value = value[:-1]
            sortedHeaders[header] = value
        except IndexError:
            pass
    return sortedHeaders

if headers:
    headers = extractHeaders(prompt())

if args.GET:
    GET = True
else:
    GET = False

headers = {}

paramList = []
try:
    with open(file, 'r') as file:
        for line in file:
            paramList.append(line.strip('\n'))
except FileNotFoundError:
    print ('%s The specified file doesn\'t exist' % bad)
    quit()


def heuristic(response, paramList):
    done = []
    forms = re.findall(r'(?i)(?s)<form.*?</form.*?>', response)
    for form in forms:
        method = re.search(r'(?i)method=[\'"](.*?)[\'"]', form)
        inputs = re.findall(r'(?i)(?s)<input.*?>', response)
        for inp in inputs:
            inpName = re.search(r'(?i)name=[\'"](.*?)[\'"]', inp)
            if inpName:
                inpType = re.search(r'(?i)type=[\'"](.*?)[\'"]', inp)
                inpValue = re.search(r'(?i)value=[\'"](.*?)[\'"]', inp)
                inpName = d(e(inpName.group(1)))
                if inpName not in done:
                    if inpName in paramList:
                        paramList.remove(inpName)
                    done.append(inpName)
                    paramList.insert(0, inpName)
                    print ('%s Heuristic found a potenial parameter: %s%s%s' % (good, green, inpName, end))
                    print ('%s Prioritizing it' % good)

url = stabilize(url)

print ('%s Analysing the content of the webpage' % run)
firstResponse = requester(url, '', headers, GET, delay)

print ('%s Now lets see how target deals with a non-existent parameter' % run)

originalFuzz = randomString(6)
data = {originalFuzz : originalFuzz[::-1]}
response = requester(url, data, headers, GET, delay)
reflections = response.text.count(originalFuzz[::-1])
print ('%s Reflections: %s%i%s' % (info, green, reflections, end))

originalHTML = response.text
originalResponse = response.text.replace(originalFuzz + '=' + originalFuzz[::-1], '')
originalCode = response.status_code
print ('%s Response Code: %s%i%s' % (info, green, originalCode, end))

newLength = len(response.text) - len(flattenParams(data))
print ('%s Content Length: %s%i%s' % (info, green, newLength, end))

print ('%s Parsing webpage for potenial parameters' % run)
heuristic(firstResponse.text, paramList)

fuzz = randomString(8)
data = {fuzz : fuzz[::-1]}
responseMulti = requester(url, data, headers, GET, delay)
multiplier = int((len(responseMulti.text.replace(fuzz + '=' + fuzz[::-1], '')) - len(response.text.replace(originalFuzz + '=' + originalFuzz[::-1], ''))) / 2)
print ('%s Content Length Multiplier: %s%i%s' % (info, green, multiplier, end))

def quickBruter(params, originalResponse, originalCode, delay, headers, url, GET): 
    newResponse = requester(url, joiner(params), headers, GET, delay)
    if newResponse.status_code != originalCode:
        return params
    elif originalResponse and originalResponse != newResponse.text:
        return params
    else:
        return False

def bruter(param, originalResponse, originalCode, multiplier, reflections, delay, headers, url, GET): 
    fuzz = randomString(6)
    data = {param : fuzz}
    response = requester(url, data, headers, GET, delay)
    newReflections = response.text.count(fuzz)
    if response.status_code != originalCode:
        print ('%s Found a valid parameter: %s%s%s' % (good, green, param, end))
        print ('%s Reason: Different response code' % info)
    elif reflections != newReflections:
        print ('%s Found a valid parameter: %s%s%s' % (good, green, param, end))
        print ('%s Reason: Different number of reflections' % info)
    elif len(response.text.replace(param + '=' + fuzz, '')) != (len(originalResponse.text.replace(originalFuzz + '=' + originalFuzz[::-1], '')) + (len(param) * multiplier)):
        print ('%s Found a valid parameter: %s%s%s' % (good, green, param, end))
        print ('%s Reason: Different content length' % info)

if firstResponse.text != originalHTML:
    originalHTML = False

print ('%s Performing heuristic level checks' % run)

def narrower(oldParamList):
    newParamList = []
    potenialParameters = 0
    threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=threadCount)
    futures = (threadpool.submit(quickBruter, part, originalHTML, originalCode, delay, headers, url, GET) for part in oldParamList)
    for i, result in enumerate(concurrent.futures.as_completed(futures)):
        if result.result():
            potenialParameters += 1
            newParamList.extend(slicer(result.result()))
        print('%s Processing: %i/%-6i' % (info, i + 1, len(oldParamList)), end='\r')
    return newParamList

toBeChecked = slicer(paramList, 25)
foundParams = []
while True:
    toBeChecked = narrower(toBeChecked)
    toBeChecked = unityExtracter(toBeChecked, foundParams)
    if not toBeChecked:
        break

if foundParams:
    print ('%s Heuristic found %i potenial parameters.' % (info, len(foundParams)))
    paramList = foundParams

threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=threadCount)
futures = (threadpool.submit(bruter, param, originalResponse, originalCode, multiplier, reflections, delay, headers, url, GET) for param in paramList)
for i, _ in enumerate(concurrent.futures.as_completed(futures)):
    print('%s Progress: %i/%i' % (info, i + 1, len(paramList)), end='\r')
print('\n%s Scan Completed' % info)
