import importlib
import unittest
from unittest.mock import Mock, patch

import arjun.core.config as mem

mem.var = {
    'rate_limit': 9999,
    'stable': False,
    'delay': 0,
    'kill': False,
    'timeout': 15,
    'disable_redirects': False,
    'include': {},
}
requester_module = importlib.import_module('arjun.core.requester')


class RequesterTests(unittest.TestCase):
    def setUp(self):
        mem.var.update({
            'stable': False,
            'delay': 0,
            'kill': False,
            'timeout': 15,
            'disable_redirects': False,
            'include': {},
        })

    @patch.object(requester_module.requests, 'get')
    def test_get_honors_redirect_setting_without_mutating_payload(self, get):
        get.return_value = Mock()
        payload = {'candidate': '1'}
        request = {
            'url': 'https://example.com',
            'method': 'GET',
            'headers': {},
            'include': {'always': 'yes'},
        }

        requester_module.requester(request, payload)

        self.assertEqual(payload, {'candidate': '1'})
        self.assertEqual(
            get.call_args.kwargs['params'],
            {'candidate': '1', 'always': 'yes'},
        )
        self.assertTrue(get.call_args.kwargs['allow_redirects'])

        mem.var['disable_redirects'] = True
        requester_module.requester(request, payload)
        self.assertFalse(get.call_args.kwargs['allow_redirects'])

    @patch.object(requester_module.requests, 'post')
    def test_xml_requests_work_without_a_template(self, post):
        post.return_value = Mock()
        request = {
            'url': 'https://example.com',
            'method': 'XML',
            'headers': {},
            'include': {},
        }

        requester_module.requester(request, {'candidate': 'value'})

        self.assertIn('<candidate>value</candidate>', post.call_args.kwargs['data'])


if __name__ == '__main__':
    unittest.main()
