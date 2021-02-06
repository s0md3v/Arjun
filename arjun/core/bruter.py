import core.config as mem

from core.anamoly import compare
from core.requester import requester
from core.error_handler import error_handler


def bruter(request, factors, params, mode='bruteforce'):
    if mem.var['kill']:
        return []
    response = requester(request, params)
    conclusion = error_handler(response, factors)
    if conclusion == 'retry':
        response = requester(request, params)
    elif conclusion == 'kill':
        return []
    comparison_result = compare(response, factors, params)
    if mode == 'verify':
        return comparison_result[0]
    return comparison_result[1]
