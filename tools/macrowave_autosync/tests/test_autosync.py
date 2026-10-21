import unittest
from unittest.mock import Mock, patch

import MacroWave_AutoSync as autosync


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


if __name__ == "__main__":
    unittest.main()
