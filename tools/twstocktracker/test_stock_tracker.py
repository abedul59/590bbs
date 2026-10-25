import importlib.util
import pathlib
import unittest
from unittest.mock import Mock


MODULE_PATH = pathlib.Path(__file__).with_name('stock_tracker.py')
SPEC = importlib.util.spec_from_file_location('stock_tracker', MODULE_PATH)
stock_tracker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(stock_tracker)


class StockTrackerTests(unittest.TestCase):
    def test_current_dashboard_and_sync_url(self):
        self.assertEqual(
            stock_tracker.DASHBOARD_URL,
            'https://590bbs.vercel.app/macrowave?view=twstocktracker',
        )
        self.assertEqual(
            stock_tracker.SYNC_TARGETS[0][1],
            'https://590bbs.vercel.app/api/twstocktracker/sync',
        )

    def test_normalizes_change_sign_without_double_negative(self):
        self.assertEqual(stock_tracker.normalize_change_percent('-', '-1.25'), '-1.25%')
        self.assertEqual(stock_tracker.normalize_change_percent('+', '1.25%'), '+1.25%')
        self.assertEqual(stock_tracker.normalize_change_percent('', '0'), '0.00%')
        self.assertIsNone(stock_tracker.normalize_change_percent('', '--'))

    def test_rejects_day_only_timestamp_and_empty_dashboard_data(self):
        with self.assertRaises(ValueError):
            stock_tracker.validate_export_payload({'date': '20261025', 'yahoo_stats': [], 'yahoo_top30': []})
        with self.assertRaises(ValueError):
            stock_tracker.validate_export_payload({'date': '20261025123045', 'yahoo_stats': [], 'yahoo_top30': []})

    def test_uploads_current_site_even_when_original_site_fails(self):
        session = Mock()
        success = Mock()
        success.raise_for_status.return_value = None
        failure = Mock()
        failure.raise_for_status.side_effect = stock_tracker.requests.HTTPError('old site failed')
        session.post.side_effect = [success, failure]
        payload = {
            'date': '20261025123045',
            'yahoo_stats': [{'market': '上市'}],
            'yahoo_top30': [],
        }

        results = stock_tracker.upload_payload(
            payload,
            targets=[('590bbs', 'https://590bbs.test/sync'), ('old', 'https://old.test/sync')],
            retries=1,
            session=session,
        )

        self.assertTrue(results['590bbs']['success'])
        self.assertFalse(results['old']['success'])
        self.assertEqual(session.post.call_count, 2)


if __name__ == '__main__':
    unittest.main()
