import unittest
from types import SimpleNamespace

import arjun.core.config as mem
from arjun.core.error_handler import error_handler


class ErrorHandlerTests(unittest.TestCase):
    def setUp(self):
        mem.var = {
            'healthy_url': True,
            'kill': False,
            'stable': False,
            'timeout': 15,
        }

    def test_successful_response_returns_ok(self):
        response = SimpleNamespace(status_code=200)
        self.assertEqual(error_handler(response, {}), 'ok')

    def test_timeout_requests_a_retry_and_increases_timeout(self):
        self.assertEqual(error_handler('ReadTimeout', {}), 'retry')
        self.assertEqual(mem.var['timeout'], 20)


if __name__ == '__main__':
    unittest.main()
