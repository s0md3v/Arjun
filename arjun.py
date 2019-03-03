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
from core.utils import e, d, stabilize, randomString, slicer, joiner, unityExtracter, getParams, flattenParams, removeTags

print ('''%s    _         
   /_| _ '    
  (  |/ /(//) %sv1.3%s
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
parser.add_argument('--include', help='include this data in every request', dest='include')
args = parser.parse_args() #arguments to be parsed

url = args.url
file = args.file or './db/params.txt'
headers = args.headers
delay = args.delay or 0
include = args.include or {}
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
else:
    headers = {}

if args.GET:
    GET = True
else:
    GET = False

include = getParams(include)

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
firstResponse = requester(url, include, headers, GET, delay)

print ('%s Now lets see how target deals with a non-existent parameter' % run)

originalFuzz = randomString(6)
data = {originalFuzz : originalFuzz[::-1]}
data.update(include)
response = requester(url, data, headers, GET, delay)
reflections = response.text.count(originalFuzz[::-1])
print ('%s Reflections: %s%i%s' % (info, green, reflections, end))

originalResponse = response.text
originalCode = response.status_code
print ('%s Response Code: %s%i%s' % (info, green, originalCode, end))

newLength = len(response.text)
plainText = removeTags(originalResponse)
plainTextLength = len(plainText)
print ('%s Content Length: %s%i%s' % (info, green, newLength, end))
print ('%s Plain-text Length: %s%i%s' % (info, green, plainTextLength, end))

factors = {'sameHTML': False, 'samePlainText': False}
if len(firstResponse.text) == len(originalResponse):
    factors['sameHTML'] = True
elif len(removeTags(firstResponse.text)) == len(plainText):
    factors['samePlainText'] = True

print ('%s Parsing webpage for potenial parameters' % run)
heuristic(firstResponse.text, paramList)

fuzz = randomString(8)
data = {fuzz : fuzz[::-1]}
data.update(include)

def quickBruter(params, originalResponse, originalCode, factors, include, delay, headers, url, GET):
    newResponse = requester(url, joiner(params, include), headers, GET, delay)
    if newResponse.status_code != originalCode:
        return params
    elif not factors['sameHTML'] and len(newResponse.text) != (len(originalResponse)):
        return params
    elif not factors['samePlainText'] and len(removeTags(originalResponse)) != len(removeTags(newResponse.text)):
        return params
    else:
        return False

def bruter(param, originalResponse, originalCode, factors, include, reflections, delay, headers, url, GET): 
    fuzz = randomString(6)
    data = {param : fuzz}
    data.update(include)
    response = requester(url, data, headers, GET, delay)
    newReflections = response.text.count(fuzz)
    reason = False
    if response.status_code != originalCode:
        reason = 'Different response code'
    elif reflections != newReflections:
        reason = 'Different number of reflections'
    elif not factors['sameHTML'] and len(response.text) != (len(originalResponse)):
        reason = 'Different content length'
    elif not factors['samePlainText'] and len(removeTags(response.text)) != (len(removeTags(originalResponse))):
        reason = 'Different plain-text content length'
    if reason:
        return {param : reason}
    else:
        return None

print ('%s Performing heuristic level checks' % run)

def narrower(oldParamList):
    newParamList = []
    potenialParameters = 0
    threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=threadCount)
    futures = (threadpool.submit(quickBruter, part, originalResponse, originalCode, factors, include, delay, headers, url, GET) for part in oldParamList)
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

finalResult = []

threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=threadCount)
futures = (threadpool.submit(bruter, param, originalResponse, originalCode, factors, include, reflections, delay, headers, url, GET) for param in foundParams)
for i, result in enumerate(concurrent.futures.as_completed(futures)):
    if result.result():
        finalResult.append(result.result())
    print('%s Progress: %i/%i' % (info, i + 1, len(paramList)), end='\r')
print('%s Scan Completed' % info)
for each in finalResult:
    for param, reason in each.items():
        print ('%s Valid parameter found: %s%s%s' % (good, green, param, end))
        print ('%s Reason: %s' % (info, reason))
