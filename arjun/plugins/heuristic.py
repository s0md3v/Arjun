import re

from arjun.core.utils import extract_js

def is_not_junk(string):
    return re.match(r'^[A-Za-z0-9_]+$', string)

def insert_words(words, wordlist, found):
    if words:
        for var in words:
            if var not in found and is_not_junk(var):
                found.append(var)
                if var in wordlist:
                    wordlist.remove(var)
                wordlist.insert(0, var)

def heuristic(response, wordlist):
    found = []
    inputs = re.findall(r'(?i)<input.+?name=["\']?([^"\'\s>]+)', response)
    insert_words(inputs, wordlist, found)
    for script in extract_js(response):
        empty_vars = re.findall(r'([^\s!=<>]+)\s*=\s*[\'"`][\'"`]', script)
        insert_words(empty_vars, wordlist, found)
        map_keys = re.findall(r'([^\'"]+)[\'"]:\s?[\'"]', script)
        insert_words(map_keys, wordlist, found)
    return found
