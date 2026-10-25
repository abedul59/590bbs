import importlib.util
import pathlib
import unittest
from unittest.mock import Mock


MODULE_PATH = pathlib.Path(__file__).with_name('bengo_auto.py')
SPEC = importlib.util.spec_from_file_location('bengo_auto', MODULE_PATH)
bengo_auto = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bengo_auto)


class BengoAutoTests(unittest.TestCase):
    def test_current_dashboard_and_upload_urls(self):
        self.assertEqual(
            bengo_auto.DASHBOARD_URL,
            'https://590bbs.vercel.app/macrowave?view=bengo',
        )
        self.assertEqual(
            bengo_auto.UPLOAD_API_URL,
            'https://590bbs.vercel.app/api/bengo/upload',
        )

    def test_threshold_boundaries(self):
        scraper = bengo_auto.BengoScraper(session=Mock())
        self.assertEqual(scraper.calculate_bengo_threshold(1000), 50)
        self.assertEqual(scraper.calculate_bengo_threshold(500), 100)
        self.assertEqual(scraper.calculate_bengo_threshold(250), 200)
        self.assertEqual(scraper.calculate_bengo_threshold(125), 400)
        self.assertEqual(scraper.calculate_bengo_threshold(62.5), 800)
        self.assertEqual(scraper.calculate_bengo_threshold(62.49), 1000)

    def test_payload_validation_filters_invalid_rows(self):
        payload = bengo_auto.build_payload('2330', '台積電', [
            {'date': '20261025', 'price': 1200, 'major_pct': 30},
            {'date': '2026-10-25', 'price': 1200},
            {'date': '20261024', 'price': 0},
        ])
        self.assertEqual(payload['stock_id'], '2330')
        self.assertEqual(len(payload['history']), 1)
        self.assertEqual(payload['dashboard_url'], bengo_auto.DASHBOARD_URL)

    def test_upload_uses_current_api_and_checks_success(self):
        session = Mock()
        response = Mock()
        response.json.return_value = {'success': True, 'count': 1, 'storage': 'database'}
        session.post.return_value = response
        payload = bengo_auto.build_payload('2330', '台積電', [{'date': '20261025', 'price': 1200}])

        result = bengo_auto.upload_payload(payload, session=session)

        self.assertTrue(result['success'])
        session.post.assert_called_once_with(
            bengo_auto.UPLOAD_API_URL,
            json=payload,
            timeout=bengo_auto.REQUEST_TIMEOUT,
        )
        response.raise_for_status.assert_called_once_with()

    def test_invalid_stock_id_is_rejected(self):
        with self.assertRaises(ValueError):
            bengo_auto.validate_stock_id('../2330')


if __name__ == '__main__':
    unittest.main()
