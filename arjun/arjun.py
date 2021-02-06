#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function

from core.colors import green, end, info, bad, good, run, res

print('''%s    _
   /_| _ '
  (  |/ /(//) v2.0-beta
      _/      %s
''' % (green, end))

try:
    from concurrent.futures import ThreadPoolExecutor, as_completed
except ImportError:
    print('%s Please use Python > 3.2 to run Arjun.' % bad)
    quit()

import sys
import json
import argparse

from urllib.parse import urlparse

import core.config as mem
from core.bruter import bruter
from core.prompt import prompt
from core.importer import importer
from core.requester import requester
from core.anamoly import define
from core.utils import fetch_params, stable_request, randomString, slicer, confirm, getParams, populate, extractHeaders, reader

from plugins.heuristic import heuristic

parser = argparse.ArgumentParser() # defines the parser
# Arguments that can be supplied
parser.add_argument('-u', help='target url', dest='url')
parser.add_argument('-o', help='path for the output file', dest='output_file')
parser.add_argument('-d', help='delay between requests', dest='delay', type=float, default=0)
parser.add_argument('-t', help='number of threads', dest='threads', type=int, default=2)
parser.add_argument('-w', help='wordlist path', dest='wordlist', default=sys.path[0]+'/db/params.txt')
parser.add_argument('-m', help='request method: GET/POST/JSON', dest='method', default='GET')
parser.add_argument('-i', help='import targets from file', dest='import_file', nargs='?', const=True)
parser.add_argument('-T', help='http request timeout', dest='timeout', type=float, default=15)
parser.add_argument('-c', help='chunk size/number of parameters to be sent at once', type=int, dest='chunks', default=500)
parser.add_argument('--headers', help='add headers', dest='headers', nargs='?', const=True)
parser.add_argument('--passive', help='collect parameter names from passive sources', dest='passive')
parser.add_argument('--stable', help='prefer stability over speed', dest='stable', action='store_true')
parser.add_argument('--include', help='include this data in every request', dest='include', default={})
args = parser.parse_args() # arguments to be parsed

mem.var = vars(args)

mem.var['method'] = mem.var['method'].upper()

if mem.var['stable'] or mem.var['delay']:
    mem.var['threads'] = 1

try:
    wordlist = set(reader(args.wordlist, mode='lines'))
    if mem.var['passive']:
        host = mem.var['passive']
        if host == '-':
            host = urlparse(args.url).netloc
        print('%s Collecting parameter names from passive sources for %s, it may take a while' % (run, host))
        passive_params = fetch_params(host)
        wordlist.update(passive_params)
        print('%s Collected %s parameters, added to the wordlist' % (info, len(passive_params)))
    wordlist = list(wordlist)
except FileNotFoundError:
    exit('%s The specified file for parameters doesn\'t exist' % bad)

if len(wordlist) < mem.var['chunks']:
   mem.var['chunks'] = int(len(wordlist)/2)

if not (args.url, args.import_file):
    exit('%s No targets specified' % bad)

def prepare_requests(args):
    headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:83.0) Gecko/20100101 Firefox/83.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'close',
    'Upgrade-Insecure-Requests': '1'
    }
    if type(headers) == bool:
        headers = extractHeaders(prompt())
    elif type(headers) == str:
        headers = extractHeaders(headers)
    if mem.var['method'] == 'JSON':
        headers['Content-type'] = 'application/json'
    if args.url:
        params = getParams(args.include)
        return {
            'url': args.url,
            'method': mem.var['method'],
            'headers': headers,
            'include': params
        }
    elif args.import_file:
        return importer(args.import_file, mem.var['method'], headers, args.include)
    return []


def narrower(request, factors, param_groups):
    anamolous_params = []
    threadpool = ThreadPoolExecutor(max_workers=mem.var['threads'])
    futures = (threadpool.submit(bruter, request, factors, params) for params in param_groups)
    for i, result in enumerate(as_completed(futures)):
        if result.result():
            anamolous_params.extend(slicer(result.result()))
        if not mem.var['kill']:
            print('%s Processing chunks: %i/%-6i' % (info, i + 1, len(param_groups)), end='\r')
    return anamolous_params

def initialize(request, wordlist):
    url = request['url']
    if not url.startswith('http'):
        print('%s %s is not a valid URL' % (bad, url))
        return 'skipped'
    print('%s Probing the target for stability' % run)
    stable = stable_request(url, request['headers'])
    if not stable:
        return 'skipped'
    else:
        fuzz = randomString(6)
        response_1 = requester(request, {fuzz : fuzz[::-1]})
        print('%s Analysing HTTP response for anamolies' % run)
        fuzz = randomString(6)
        response_2 = requester(request, {fuzz : fuzz[::-1]})
        if type(response_1) == str or type(response_2) == str:
            return 'skipped'
        factors = define(response_1, response_2, fuzz, fuzz[::-1], wordlist)
        print('%s Analysing HTTP response for potential parameter names' % run)
        found = heuristic(response_1.text, wordlist)
        if found:
            num = len(found)
            s = 's' if num > 1 else ''
            print('%s Heuristic scanner found %i parameter%s: %s' % (good, num, s, ', '.join(found)))
        print('%s Logicforcing the URL endpoint' % run)
        populated = populate(wordlist)
        param_groups = slicer(populated, int(len(wordlist)/mem.var['chunks']))
        last_params = []
        while True:
            param_groups = narrower(request, factors, param_groups)
            if mem.var['kill']:
                return 'skipped'
            param_groups = confirm(param_groups, last_params)
            if not param_groups:
                break
        confirmed_params = []
        for param in last_params:
            reason = bruter(request, factors, param, mode='verify')
            if reason:
                name = list(param.keys())[0]
                confirmed_params.append(name)
                print('%s name: %s, factor: %s' % (res, name, reason))
        return confirmed_params

request = prepare_requests(args)

final_result = {}

try:
    if type(request) == dict:
        mem.var['kill'] = False
        url = request['url']
        these_params = initialize(request, wordlist)
        if these_params == 'skipped':
            print('%s Skipped %s due to errors' % (bad, request['url']))
        elif these_params:
            final_result['url'] = url
            final_result['params'] = these_params
            final_result['method'] = request['method']
    elif type(request) == list:
        for each in request:
            url = each['url']
            mem.var['kill'] = False
            print('%s Scanning: %s' % (run, url))
            these_params = initialize(each, list(wordlist))
            if these_params == 'skipped':
                print('%s Skipped %s due to errors' % (bad, url))
            elif these_params:
                final_result[url] = {}
                final_result[url]['params'] = these_params
                final_result[url]['method'] = each['method']
                print('%s Parameters found: %s' % (good, ', '.join(final_result[url])))
except KeyboardInterrupt:
    exit()

# Finally, export to json
if args.output_file and final_result:
    with open(str(mem.var['output_file']), 'w+', encoding='utf8') as json_output:
        json.dump(final_result, json_output, sort_keys=True, indent=4)
    print('%s Output saved to JSON file in %s' % (info, mem.var['output_file']))
