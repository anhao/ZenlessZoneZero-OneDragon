"""Regression tests for WPUSH channel HTTP handling."""

from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

cv2 = types.ModuleType("cv2")
cv2_typing = types.ModuleType("cv2.typing")
cv2_typing.MatLike = object
cv2.typing = cv2_typing
sys.modules.setdefault("cv2", cv2)
sys.modules.setdefault("cv2.typing", cv2_typing)

ROOT = Path(__file__).resolve().parents[2] / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from one_dragon.base.push.channel.wpush import WPush  # noqa: E402


class TestWPushHttpHandling(unittest.TestCase):
    def setUp(self) -> None:
        self.channel = WPush()
        self.config = {"APIKEY": "WPUSHtestkey", "CHANNEL": "wechat", "TOPIC_CODE": ""}

    def _mock_response(self, status_code: int, payload: dict) -> MagicMock:
        resp = MagicMock()
        resp.status_code = status_code
        resp.json.return_value = payload
        return resp

    @patch("one_dragon.base.push.channel.wpush.requests.post")
    def test_success_on_http_200_code_0(self, mock_post: MagicMock) -> None:
        mock_post.return_value = self._mock_response(200, {"code": 0, "message": "success"})
        ok, msg = self.channel.push(self.config, "t", "c")
        self.assertTrue(ok)
        self.assertIn("成功", msg)
        kwargs = mock_post.call_args.kwargs
        self.assertFalse(kwargs.get("allow_redirects", True))
        self.assertIn("proxies", kwargs)

    @patch("one_dragon.base.push.channel.wpush.requests.post")
    def test_reject_307_even_if_body_code_0(self, mock_post: MagicMock) -> None:
        mock_post.return_value = self._mock_response(307, {"code": 0, "message": "redirect"})
        ok, msg = self.channel.push(self.config, "t", "c")
        self.assertFalse(ok)
        self.assertIn("HTTP 307", msg)

    @patch("one_dragon.base.push.channel.wpush.requests.post")
    def test_reject_308_even_if_body_code_0(self, mock_post: MagicMock) -> None:
        mock_post.return_value = self._mock_response(308, {"code": 0, "message": "redirect"})
        ok, msg = self.channel.push(self.config, "t", "c")
        self.assertFalse(ok)
        self.assertIn("HTTP 308", msg)


if __name__ == "__main__":
    unittest.main()
