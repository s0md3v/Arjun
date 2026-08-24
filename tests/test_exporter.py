import json

import arjun.core.config as mem
from arjun.core.exporter import build_raw_request, raw_export


def _headers():
    return {'User-Agent': 'test-agent', 'Connection': 'close'}


def test_raw_request_get():
    data = {'method': 'GET', 'params': ['foo', 'bar'], 'headers': _headers()}
    raw = build_raw_request('http://example.com/api', data)
    lines = raw.split('\r\n')
    assert lines[0].startswith('GET /api?')
    assert lines[0].endswith(' HTTP/1.1')
    assert 'foo=' in lines[0] and 'bar=' in lines[0]
    assert 'Host: example.com' in lines
    assert 'User-Agent: test-agent' in lines
    # GET has no body, so the request ends with a blank line
    assert raw.endswith('\r\n\r\n')


def test_raw_request_get_keeps_existing_query():
    data = {'method': 'GET', 'params': ['foo'], 'headers': _headers()}
    raw = build_raw_request('http://example.com/api?a=1', data)
    request_line = raw.split('\r\n')[0]
    assert 'a=1' in request_line
    assert 'foo=' in request_line


def test_raw_request_post_form():
    data = {'method': 'POST', 'params': ['foo'], 'headers': _headers()}
    raw = build_raw_request('http://example.com/login', data)
    head, body = raw.split('\r\n\r\n', 1)
    assert head.split('\r\n')[0] == 'POST /login HTTP/1.1'
    assert 'Content-Type: application/x-www-form-urlencoded' in head
    assert 'Content-Length: %d' % len(body) in head
    assert body.startswith('foo=')


def test_raw_request_json():
    data = {'method': 'JSON', 'params': ['foo', 'bar'], 'headers': _headers()}
    raw = build_raw_request('http://example.com/v1', data)
    head, body = raw.split('\r\n\r\n', 1)
    assert head.split('\r\n')[0] == 'POST /v1 HTTP/1.1'
    assert 'Content-Type: application/json' in head
    parsed = json.loads(body)
    assert set(parsed.keys()) == {'foo', 'bar'}


def test_raw_request_empty_path():
    data = {'method': 'GET', 'params': ['foo'], 'headers': _headers()}
    raw = build_raw_request('http://example.com', data)
    assert raw.split('\r\n')[0].startswith('GET /?foo=')


def test_raw_export_writes_file(tmp_path):
    out = tmp_path / 'raw.txt'
    mem.var = {'raw_file': str(out)}
    result = {'http://example.com/api': {'method': 'GET', 'params': ['foo'], 'headers': _headers()}}
    raw_export(result)
    content = out.read_text()
    assert 'GET /api?foo=' in content
    assert 'Host: example.com' in content
