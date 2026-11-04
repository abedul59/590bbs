import json
import os
import tempfile
import unittest
from unittest.mock import Mock, patch

import pandas as pd

import MacroWave_AutoSync as autosync


class ConfigTests(unittest.TestCase):
    def load_from_directory(self, directory, environment=None):
        with patch.object(autosync, "get_app_dir", return_value=directory), patch.object(
            autosync.os, "getcwd", return_value=directory
        ), patch.dict(os.environ, environment or {}, clear=True):
            return autosync.load_config()

    def test_example_placeholder_is_not_treated_as_a_fred_key(self):
        with tempfile.TemporaryDirectory() as directory:
            with open(os.path.join(directory, "macrowave_config.json"), "w", encoding="utf-8") as config_file:
                json.dump({"fred_api_key": "請填入您的 FRED API Key"}, config_file)

            self.assertEqual(self.load_from_directory(directory)["fred_api_key"], "")

    def test_blank_environment_value_falls_back_to_config_file(self):
        with tempfile.TemporaryDirectory() as directory:
            with open(os.path.join(directory, "macrowave_config.json"), "w", encoding="utf-8") as config_file:
                json.dump({"fred_api_key": "configured-key"}, config_file)

            config = self.load_from_directory(directory, {"FRED_API_KEY": "   "})
            self.assertEqual(config["fred_api_key"], "configured-key")

    def test_supports_uppercase_key_in_example_file(self):
        with tempfile.TemporaryDirectory() as directory:
            config_path = os.path.join(directory, "macrowave_config.example.json")
            with open(config_path, "w", encoding="utf-8") as config_file:
                json.dump({"FRED_API_KEY": "configured-key"}, config_file)

            config = self.load_from_directory(directory)
            self.assertEqual(config["fred_api_key"], "configured-key")
            self.assertEqual(config["fred_api_key_source"], config_path)

    def test_finds_json_in_launch_directory_when_exe_directory_differs(self):
        with tempfile.TemporaryDirectory() as exe_directory, tempfile.TemporaryDirectory() as launch_directory:
            config_path = os.path.join(launch_directory, "macrowave_config.json")
            with open(config_path, "w", encoding="utf-8") as config_file:
                json.dump({"fredApiKey": "configured-key"}, config_file)

            with patch.object(autosync, "get_app_dir", return_value=exe_directory), patch.object(
                autosync.os, "getcwd", return_value=launch_directory
            ), patch.dict(os.environ, {}, clear=True):
                config = autosync.load_config()

            self.assertEqual(config["fred_api_key"], "configured-key")
            self.assertEqual(config["fred_api_key_source"], config_path)


class Mark17Tests(unittest.TestCase):
    def make_logic(self, gap=5.0, bei=3.0):
        logic = autosync.MacroWaveMark17_Logic.__new__(autosync.MacroWaveMark17_Logic)
        logic.get_us_pmi_from_news = Mock(return_value=[49.0])
        logic.get_us_inflation_gap = Mock(return_value=gap)
        logic.get_us_bei = Mock(return_value=bei)
        return logic

    def test_maximum_score_is_15_without_double_counting_unemployment(self):
        score, details = self.make_logic().calculate_score(
            {"Spread_3M_10Y": -1},
            {"M1b_YoY": -1, "MV_Ratio": 3, "Recession_Prob": "30%"},
            {"Unemployment": 5},
        )

        self.assertEqual(score, 15)
        unemployment_scores = [item_score for item, _value, item_score in details if item.startswith("失業率")]
        self.assertEqual(unemployment_scores, ["+2", "0 (已計入 > 4.5%)"])

    def test_missing_fred_data_is_marked_unavailable(self):
        score, details = self.make_logic(gap=None, bei=None).calculate_score(
            {"Spread_3M_10Y": 1},
            {"M1b_YoY": 1, "MV_Ratio": 1, "Recession_Prob": "10%"},
            {"Unemployment": 3},
        )
        result = autosync.MacroWaveJSON_Logic().generate_json(
            {}, {}, {}, {}, [], [], [], score, "", details
        )

        self.assertFalse(result["mark17_complete"])
        fred_rows = [row for row in result["mark17"] if "FRED" in str(row["value"])]
        self.assertEqual(len(fred_rows), 2)
        self.assertTrue(all(row["status"] == "Unavailable" for row in fred_rows))

    def test_missing_yield_and_recession_are_unavailable_not_zero_risk(self):
        score, details = self.make_logic(gap=0, bei=2).calculate_score(
            {"Spread_3M_10Y": None},
            {"M1b_YoY": 1, "MV_Ratio": 1, "Recession_Prob": "N/A"},
            {"Unemployment": 3},
        )

        unavailable = [row for row in details if row[2] == "-"]
        self.assertTrue(any(row[0] == "殖利率倒掛" for row in unavailable))
        self.assertTrue(any(row[0] == "衰退機率 > 20%" for row in unavailable))


class FredObservationTests(unittest.TestCase):
    def test_latest_non_empty_fred_value_and_date(self):
        fred = Mock()
        fred.get_series.return_value = pd.Series(
            [4.1, None, 4.25],
            index=pd.to_datetime(["2026-10-30", "2026-11-01", "2026-11-03"]),
        )

        date_str, value = autosync.latest_fred_observation(
            fred, "DGS10", max_age_days=14, now="2026-11-04"
        )

        self.assertEqual(date_str, "2026-11-03")
        self.assertEqual(value, 4.25)

    def test_stale_fred_value_is_rejected(self):
        fred = Mock()
        fred.get_series.return_value = pd.Series(
            [12.76], index=pd.to_datetime(["2022-09-01"])
        )

        self.assertEqual(
            autosync.latest_fred_observation(
                fred, "RECPROUSM156N", max_age_days=180, now="2026-11-04"
            ),
            (None, None),
        )

    def test_us_yields_prefer_fred_and_include_observation_dates(self):
        fred = Mock()
        fred.get_series.side_effect = [
            pd.Series([3.75], index=pd.to_datetime(["2026-11-03"])),
            pd.Series([4.25], index=pd.to_datetime(["2026-11-03"])),
        ]
        logic = autosync.MacroWaveA_Logic.__new__(autosync.MacroWaveA_Logic)
        logic.fred = fred
        logic.headers = {}

        with patch.object(autosync.datetime, "datetime", wraps=autosync.datetime.datetime) as dt:
            dt.now.return_value = autosync.datetime.datetime(2026, 11, 4)
            three_month, ten_year, metadata = logic.get_us_bond_yields()

        self.assertEqual((three_month, ten_year), (3.75, 4.25))
        self.assertEqual(metadata, {"3M": "2026-11-03", "10Y": "2026-11-03", "source": "FRED"})

    def test_recession_probability_prefers_current_fred_value(self):
        fred = Mock()
        fred.get_series.return_value = pd.Series(
            [8.5], index=pd.to_datetime(["2026-10-01"])
        )
        logic = autosync.MacroWaveBC_Logic.__new__(autosync.MacroWaveBC_Logic)
        logic.fred = fred

        with patch.object(autosync.datetime, "datetime", wraps=autosync.datetime.datetime) as dt:
            dt.now.return_value = autosync.datetime.datetime(2026, 11, 4)
            self.assertEqual(logic.get_recession_prob(), ("2026-10-01", "8.50%"))


class LeadingIndicatorTests(unittest.TestCase):
    def test_parses_conference_board_leading_index_without_using_percent_change(self):
        text = "The U.S. LEI fell by 0.3 percent in September to 98.4 (2016=100)."

        self.assertEqual(autosync.MacroWaveBC_Logic.parse_us_leading_index(text), "98.4")

    def test_returns_none_when_text_only_contains_a_percentage(self):
        text = "The Leading Economic Index declined 0.3 percent during the month."

        self.assertIsNone(autosync.MacroWaveBC_Logic.parse_us_leading_index(text))


class UploadJsonTests(unittest.TestCase):
    @patch.object(autosync.requests, "post")
    def test_accepts_any_success_status(self, post):
        post.return_value = Mock(status_code=204, text="")

        result = autosync.upload_json(
            "590bbs",
            "https://590bbs.vercel.app/api/macrowave/upload",
            {"value": 1},
            {"X-Api-Key": "test"},
        )

        self.assertTrue(result)
        post.assert_called_once()

    @patch.object(autosync.requests, "post", side_effect=TimeoutError("timeout"))
    def test_network_failure_does_not_raise(self, _post):
        self.assertFalse(autosync.upload_json("offline", "https://example.invalid", {}, {}))

    @patch.object(autosync.requests, "post")
    def test_retries_http_400_as_json_file_when_enabled(self, post):
        post.side_effect = [
            Mock(status_code=400, text='{"status":"error","message":"未找到有效數據"}'),
            Mock(status_code=200, text='{"status":"success"}'),
        ]

        result = autosync.upload_json(
            "Render",
            "https://macrowave-web.onrender.com/api/upload/",
            {"date": "2026-10-23", "value": "中文"},
            {"X-Api-Key": "test"},
            multipart_fallback=True,
        )

        self.assertTrue(result)
        self.assertEqual(post.call_count, 2)
        retry_files = post.call_args_list[1].kwargs["files"]
        filename, content, content_type = retry_files["file"]
        self.assertEqual(filename, "macrowave_data.json")
        self.assertEqual(content_type, "application/json")
        self.assertEqual(json.loads(content.decode("utf-8"))["value"], "中文")


if __name__ == "__main__":
    unittest.main()
