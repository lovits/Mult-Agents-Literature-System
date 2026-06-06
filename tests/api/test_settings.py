from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from app.core.config import Settings


class SettingsTest(unittest.TestCase):
    def test_defaults_are_local_and_frontend_free(self) -> None:
        settings = Settings.from_env()

        self.assertEqual(settings.redis_url, "redis://localhost:6379/0")
        self.assertEqual(settings.queue_name, "evireview")
        self.assertTrue(str(settings.sqlite_path).endswith("storage/evireview.sqlite3"))

    def test_environment_overrides(self) -> None:
        with patch.dict(
            os.environ,
            {
                "EVIREVIEW_SQLITE_PATH": "/tmp/custom.sqlite3",
                "EVIREVIEW_REDIS_URL": "redis://localhost:6380/2",
                "EVIREVIEW_QUEUE_NAME": "custom",
            },
            clear=False,
        ):
            settings = Settings.from_env()

        self.assertEqual(str(settings.sqlite_path), "/tmp/custom.sqlite3")
        self.assertEqual(settings.redis_url, "redis://localhost:6380/2")
        self.assertEqual(settings.queue_name, "custom")


if __name__ == "__main__":
    unittest.main()
