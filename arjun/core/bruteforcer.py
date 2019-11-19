"""The brute forcer of Arjun."""
import time

import arjun.core.config
from arjun.core.requester import requester
from arjun.core.utils import joiner, random_string, remove_tags


def quick_brute_force(
    params,
    original_response,
    original_code,
    reflections,
    factors,
    include,
    delay,
    headers,
    url,
    get
):
    """Quick brute forcer."""
    joined = joiner(params, include)
    new_response = requester(url, joined, headers, get, delay)
    if new_response.status_code == 429:
        if core.config.global_vars['stable']:
            print('%s Hit rate limit, stabilizing the connection..')
            time.sleep(30)
            return params
        else:
            print('%s Target has rate limiting in place, please use --stable switch' % bad)
            raise ConnectionError
    if new_response.status_code != original_code:
        return params
    elif factors['same_html'] and len(new_response.text) != (len(original_response)):
        return params
    elif factors['same_plain_text'] and len(remove_tags(original_response)) != len(remove_tags(new_response.text)):
        return params
    elif True:
        for param, value in joined.items():
            if param not in include and new_response.text.count(value) != reflections:
                return params
    else:
        return False
