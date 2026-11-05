import importlib.util
import pathlib
import shutil
import unittest
from unittest.mock import Mock, patch


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

    def test_chrome_start_retries_with_isolated_profiles(self):
        settings = dict(bengo_auto.DEFAULT_SETTINGS)
        settings.update({
            'browser_start_attempts': 3,
            'browser_start_retry_seconds': 0,
        })
        scraper = bengo_auto.BengoScraper(settings=settings, session=Mock())
        driver = Mock()

        with patch.object(
            bengo_auto.webdriver,
            'Chrome',
            side_effect=[RuntimeError('chrome not reachable'), driver],
        ) as chrome:
            result, profile_dir = scraper.start_chrome()

        try:
            self.assertIs(result, driver)
            self.assertEqual(chrome.call_count, 2)
            first_options = chrome.call_args_list[0].kwargs['options']
            second_options = chrome.call_args_list[1].kwargs['options']
            first_profile = next(arg for arg in first_options.arguments if arg.startswith('--user-data-dir='))
            second_profile = next(arg for arg in second_options.arguments if arg.startswith('--user-data-dir='))
            self.assertNotEqual(first_profile, second_profile)
            self.assertIn('--remote-debugging-pipe', second_options.arguments)
        finally:
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
