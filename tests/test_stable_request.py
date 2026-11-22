"""
Regression test for stable_request() incorrectly aborting parameter
discovery entirely on a reachable URL just because its Content-Type isn't
one of a small hardcoded allowlist (text/html/json/xml) -- see issue #222.

Nothing downstream of stable_request() actually requires a text content
type: anomaly detection in arjun/core/anomaly.py diffs response.text
(which `requests` always decodes to a string) and response length/status,
regardless of what Content-Type the server sent. The old behavior silently
dropped the entire target URL from scanning; the fix is to warn and
continue instead.
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import arjun.core.config as mem
from arjun.core.utils import stable_request


def _mock_response(content_type, url="https://target.test/download"):
    response = MagicMock()
    response.headers = {"Content-Type": content_type} if content_type else {}
    response.url = url
    return response


@patch("arjun.core.utils.requests.get")
def test_stable_request_continues_on_octet_stream(mock_get):
    mem.var["disable_redirects"] = False
    mock_get.return_value = _mock_response("application/octet-stream")

    result = stable_request("https://target.test/download", {})

    assert result == "https://target.test/download"


@patch("arjun.core.utils.requests.get")
def test_stable_request_continues_with_no_content_type_header(mock_get):
    mem.var["disable_redirects"] = False
    mock_get.return_value = _mock_response(None)

    result = stable_request("https://target.test/download", {})

    assert result == "https://target.test/download"


@patch("arjun.core.utils.requests.get")
def test_stable_request_still_works_for_normal_html(mock_get):
    mem.var["disable_redirects"] = False
    mock_get.return_value = _mock_response("text/html; charset=utf-8", url="https://target.test/page")

    result = stable_request("https://target.test/page", {})

    assert result == "https://target.test/page"


@patch("arjun.core.utils.requests.get")
def test_stable_request_still_works_for_json(mock_get):
    mem.var["disable_redirects"] = False
    mock_get.return_value = _mock_response("application/json", url="https://target.test/api")

    result = stable_request("https://target.test/api", {})

    assert result == "https://target.test/api"


@patch("arjun.core.utils.requests.get")
def test_stable_request_returns_none_on_connection_failure(mock_get):
    mem.var["disable_redirects"] = False
    mock_get.side_effect = Exception("ConnectionError: refused")

    result = stable_request("https://target.test/down", {})

    assert result is None
