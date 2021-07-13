import re
import requests

from arjun.core.utils import diff_map, remove_tags


def define(response_1, response_2, param, value, wordlist):
    """
    defines a rule list for detecting anomalies by comparing two HTTP response
    returns dict
    """
    factors = {
        'same_code': False, # if http status code is same, contains that code
        'same_body': False, # if http body is same, contains that body
        'same_plaintext': False, # if http body isn't same but is same after removing html, contains that non-html text
        'lines_num': False, # if number of lines in http body is same, contains that number
        'lines_diff': False, # if http-body or plaintext aren't and there are more than two lines, contain which lines are same
        'same_headers': False, # if the headers are same, contains those headers
        'same_redirect': False, # if both requests redirect in similar manner, contains that redirection
        'param_missing': False, # if param name is missing from the body, contains words that are already there
        'value_missing': False # contains whether param value is missing from the body
    }
    if type(response_1) == type(response_2) == requests.models.Response:
        body_1, body_2 = response_1.text, response_2.text
        if response_1.status_code == response_2.status_code:
            factors['same_code'] = response_1.status_code
        if response_1.headers.keys() == response_2.headers.keys():
            factors['same_headers'] = list(response_1.headers.keys())
        if response_1.url == response_2.url:
            factors['same_redirect'] = response_1.url
        if response_1.text == response_2.text:
            factors['same_body'] = response_1.text
        elif response_1.text.count('\n') == response_2.text.count('\n'):
            factors['lines_num'] = response_1.text.count('\n')
        elif remove_tags(body_1) == remove_tags(body_2):
            factors['same_plaintext'] = remove_tags(body_1)
        elif body_1 and body_2 and body_1.count('\\n') == body_2.count('\\n'):
                factors['lines_diff'] = diff_map(body_1, body_2)
        if param not in response_2.text:
            factors['param_missing'] = [word for word in wordlist if word in response_2.text]
        if value not in response_2.text:
            factors['value_missing'] = True
    return factors


def compare(response, factors, params):
    """
    detects anomalies by comparing a HTTP response against a rule list
    returns string, list (anomaly, list of parameters that caused it)
    """
    if factors['same_code'] and response.status_code != factors['same_code']:
        return ('http code', params)
    if factors['same_headers'] and list(response.headers.keys()) != factors['same_headers']:
        return ('http headers', params)
    if factors['same_redirect'] and response.url != factors['same_redirect']:
        return ('redirection', params)
    if factors['same_body'] and response.text != factors['same_body']:
        return ('body length', params)
    if factors['lines_num'] and response.text.count('\n') != factors['lines_num']:
        return ('number of lines', params)
    if factors['same_plaintext'] and remove_tags(response.text) != factors['same_plaintext']:
        return ('text length', params)
    if factors['lines_diff']:
        for line in factors['lines_diff']:
            if line not in response.text:
                return ('lines', params)
    if type(factors['param_missing']) == list:
        for param in params.keys():
            if param in response.text and param not in factors['param_missing'] and re.search(r'[\'"\s]%s[\'"\s]' % param, response.text):
                return ('param name reflection', params)
    if factors['value_missing']:
        for value in params.values():
            if value in response.text and re.search(r'[\'"\s]%s[\'"\s]' % value, response.text):
                return ('param value reflection', params)
    return ('', [])
