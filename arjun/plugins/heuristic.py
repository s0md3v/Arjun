import re

from arjun.core.utils import extract_js

re_not_junk = re.compile(r'^[A-Za-z0-9_]+$')


def is_not_junk(param):
    return (re_not_junk.match(param) is not None)

# TODO: for map keys, javascript tolerates { param: "value" }
re_input_names = re.compile(r'''(?i)<input.+?name=["']?([^"'\s>]+)''')
re_input_ids = re.compile(r'''(?i)<input.+?id=["']?([^"'\s>]+)''')
re_empty_vars = re.compile(r'''(?:[;\n]|\bvar|\blet)(\w+)\s*=\s*(?:['"`]{1,2}|true|false|null)''')
re_map_keys = re.compile(r'''['"](\w+?)['"]\s*:\s*['"`]''')


def heuristic(response, wordlist):
    potential_params = []

    # Parse Inputs
    input_names = re_input_names.findall(response)
    potential_params += input_names

    input_ids = re_input_ids.findall(response)
    potential_params += input_ids

    # Parse Scripts
    for script in extract_js(response):
        empty_vars = re_empty_vars.findall(script)
        potential_params += empty_vars

        map_keys = re_map_keys.findall(script)
        potential_params += map_keys

    if len(potential_params) == 0:
        return []

    found = set()
    for word in potential_params:
        if is_not_junk(word) and (word not in found):
            found.add(word)

            if word in wordlist:
                wordlist.remove(word)
            wordlist.insert(0, word)

    return list(found)
