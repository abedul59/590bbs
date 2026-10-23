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
