import unittest

from utils.config import normalize_targets, parse_tasks


class ConfigTests(unittest.TestCase):
    def test_parse_tasks_tolerates_literal_newline_in_target(self):
        raw_tasks = '[{"username":"测试用户","targets":["BLG-黄任行\n"]}]'

        tasks = parse_tasks(raw_tasks)

        self.assertEqual(tasks[0]["targets"], ["BLG-黄任行\n"])
        self.assertEqual(
            normalize_targets(tasks[0]["targets"], tasks[0]["username"]),
            ["BLG-黄任行"],
        )

    def test_parse_tasks_requires_array(self):
        with self.assertRaisesRegex(ValueError, "JSON 数组"):
            parse_tasks('{"targets": []}')


if __name__ == "__main__":
    unittest.main()
