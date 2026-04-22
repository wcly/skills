import unittest
from pathlib import Path


ROOT = Path("/Users/ut/Documents/learn/skills/juejin-auto-checkin")


class InstallPathTests(unittest.TestCase):
    def test_wrapper_does_not_hardcode_workspace_script_path(self):
        wrapper = (ROOT / "scripts" / "juejin_auto_wrapper.sh").read_text(encoding="utf-8")

        self.assertNotIn(
            "/Users/ut/Documents/learn/skills/juejin-auto-checkin/scripts/juejin_auto.py",
            wrapper,
        )

    def test_cron_manager_does_not_reference_legacy_install_locations(self):
        cron_manager = (ROOT / "scripts" / "cron_manager.py").read_text(encoding="utf-8")

        self.assertNotIn("/Users/ut/.trae-cn/skills/juejin-auto-checkin", cron_manager)


if __name__ == "__main__":
    unittest.main()
