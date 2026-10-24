import importlib.util
import pathlib
import unittest
from unittest.mock import Mock, patch


MODULE_PATH = pathlib.Path(__file__).with_name("PER_auto.py")
SPEC = importlib.util.spec_from_file_location("per_auto", MODULE_PATH)
per_auto = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(per_auto)


class PerAutoTests(unittest.TestCase):
    def test_safe_filename_removes_windows_invalid_characters(self):
        self.assertEqual(per_auto.safe_filename('2330_台積/電:*?"<>|.json'), "2330_台積_電_______.json")

    def test_q3_and_q4_use_next_year_forward_valuation(self):
        self.assertEqual(per_auto.determine_forecast_year(2026, 10, 9), 2027)
        self.assertEqual(per_auto.determine_forecast_year(2026, 8, 8), 2026)

    def test_next_year_revenue_is_based_on_completed_current_year(self):
        base, forecast = per_auto.calculate_revenue_forecast(
            [10] * 12,
            0.10,
            10,
            forecast_next_year=True,
        )
        self.assertEqual(base, 122.0)
        self.assertEqual(forecast, 134.2)

    def test_eps_uses_same_year_revenue_margin_and_capital(self):
        self.assertEqual(per_auto.calculate_eps_forecast(134.2, 0.12, 30), 5.37)

    def test_2330_like_data_scores_all_six_indicators(self):
        ratings = [
            per_auto.rate_revenue([54.65, 53.32, 44.69, 67.87, 30.09, 17.50])[0],
            per_auto.rate_operating_margin([60.34, 58.10, 54.00, 50.58])[0],
            per_auto.rate_net_income([641997, 577941, 514593, 458831, 386382, 364042, 379332, 323459])[0],
            per_auto.rate_eps([27.25, 22.08, 19.51, 17.44])[0],
            per_auto.rate_inventory_turnover([12.76, 11.37, 10.44, 11.85, 11.69])[0],
            per_auto.rate_free_cash_flow([725509, 625574, 497064, 426829, 620205, 391992])[0],
        ]

        self.assertEqual(ratings, ['AA'] * 6)
        self.assertEqual(per_auto.average_rating(ratings), 4.0)

    def test_financial_series_matches_labels_without_column_offset(self):
        html = """
        <div class="table-row"><span>項目</span><span>2026.2Q</span><span>2026.1Q</span></div>
        <div class="table-row"><span>營業利益率</span><span>60.34%</span><span>58.10%</span></div>
        """
        soup = per_auto.BeautifulSoup(html, 'html.parser')

        self.assertEqual(
            per_auto.find_financial_series(soup, ('營業利益率',)),
            [('2026.2Q', 60.34), ('2026.1Q', 58.10)],
        )

    @patch.object(per_auto.requests, "get")
    def test_latest_price_uses_yahoo_chart(self, get):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            'chart': {'result': [{'meta': {'regularMarketPrice': 1495}}]}
        }
        get.return_value = response

        self.assertEqual(per_auto.get_latest_price('2330'), 1495.0)
        self.assertIn('2330.TW', get.call_args.args[0])

    def test_source_urls_are_stock_specific_and_auditable(self):
        sources = per_auto.build_source_urls('2330')

        self.assertIn('2330', sources['Revenue'])
        self.assertIn('2330', sources['QuarterlyIncome'])
        self.assertIn('2330', sources['Capital'])
        self.assertIn('stockNo=2330', sources['TWSEAnnualPrice'])
        self.assertTrue(sources['YahooQuote'].endswith('/2330'))

    @patch.object(per_auto.requests, "post")
    def test_uploads_to_both_dashboards(self, post):
        response = Mock()
        response.raise_for_status.return_value = None
        post.return_value = response

        result = per_auto.upload_payload({"2330": {"Meta": {}}}, retries=1)

        self.assertEqual(post.call_count, 2)
        self.assertTrue(all(result.values()))
        self.assertEqual(
            [call.args[0] for call in post.call_args_list],
            [url for _, url in per_auto.UPLOAD_TARGETS],
        )


if __name__ == "__main__":
    unittest.main()
