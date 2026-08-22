import sys
import types
import unittest
from unittest.mock import patch


playwright_module = types.ModuleType("playwright")
sync_api_module = types.ModuleType("playwright.sync_api")
sync_api_module.Response = object
sync_api_module.sync_playwright = lambda: None
sys.modules.setdefault("playwright", playwright_module)
sys.modules.setdefault("playwright.sync_api", sync_api_module)

browser_module = types.ModuleType("core.browser")
browser_module.get_browser = lambda: (None, None)
sys.modules["core.browser"] = browser_module

message_module = types.ModuleType("core.msg_builder")
message_module.build_message = lambda: "test message"
sys.modules["core.msg_builder"] = message_module

from core import tasks


class FakeChatInput:
    def type(self, _text):
        pass

    def press(self, _key):
        pass


class FakePage:
    url = "https://www.douyin.com/chat"

    def on(self, *_args):
        pass

    def goto(self, *_args, **_kwargs):
        pass

    def wait_for_selector(self, *_args, **_kwargs):
        pass

    def locator(self, _selector):
        return FakeChatInput()

    def screenshot(self, *_args, **_kwargs):
        pass

    def title(self):
        return "Douyin"


class FakeContext:
    def __init__(self):
        self.page = FakePage()

    def set_default_navigation_timeout(self, _timeout):
        pass

    def set_default_timeout(self, _timeout):
        pass

    def new_page(self):
        return self.page

    def add_cookies(self, _cookies):
        pass

    def close(self):
        pass


class FakeBrowser:
    def new_context(self):
        return FakeContext()


class FakeResponse:
    url = "https://www.douyin.com/aweme/v1/web/im/user/info"

    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload


class TasksTests(unittest.TestCase):
    def test_null_response_data_is_ignored(self):
        tasks.handle_response(FakeResponse({"data": None}))

    @patch.object(tasks, "save_failure_diagnostics")
    @patch.object(tasks, "scroll_and_select_user", return_value=iter(()))
    def test_no_matching_targets_fails_the_task(self, _select, diagnostics):
        with self.assertRaisesRegex(RuntimeError, "0/2"):
            tasks.do_user_task(FakeBrowser(), "account", [], ["one", "two"])
        diagnostics.assert_called_once()

    @patch.object(
        tasks,
        "scroll_and_select_user",
        return_value=iter(("one", "two")),
    )
    def test_all_targets_returns_sent_count(self, _select):
        sent_count = tasks.do_user_task(
            FakeBrowser(), "account", [], ["one", "two"]
        )
        self.assertEqual(sent_count, 2)


if __name__ == "__main__":
    unittest.main()
