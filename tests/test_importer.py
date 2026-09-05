import tempfile
import unittest

from arjun.core.importer import importer, parse_headers


class ImporterTests(unittest.TestCase):
    def test_header_values_may_contain_colons(self):
        self.assertEqual(
            parse_headers('Host: example.com\nAuthorization: token:a:b'),
            {'Host': 'example.com', 'Authorization': 'token:a:b'},
        )

    def test_url_import_preserves_included_parameters(self):
        with tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8') as targets:
            targets.write('https://example.com/api\n')
            targets.flush()
            requests = importer(targets.name, 'GET', {}, {'session': 'one'})

        self.assertEqual(requests[0]['include'], {'session': 'one'})


if __name__ == '__main__':
    unittest.main()
