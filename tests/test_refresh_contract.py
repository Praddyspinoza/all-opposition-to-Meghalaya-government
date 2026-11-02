import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class RefreshContractTests(unittest.TestCase):
    def test_early_backup_schedules_and_external_trigger(self):
        workflow = (ROOT / '.github/workflows/daily-sources.yml').read_text()
        self.assertIn("cron: '13 23 * * *'", workflow)
        self.assertIn("cron: '17 0 * * *'", workflow)
        self.assertIn('workflow_dispatch:', workflow)
        self.assertIn('cancel-in-progress: false', workflow)
        self.assertIn('contents: write', workflow)
        self.assertIn('git add daily_sources.json', workflow)
        self.assertIn('Validate refreshed feed', workflow)

    def test_collector_and_frontend_metadata_contract(self):
        script = (ROOT / 'scripts/collect_sources.py').read_text()
        page = (ROOT / 'index.html').read_text()
        self.assertIn('last_checked_utc', script)
        self.assertIn("(d[0].last_checked_utc||", page)
        self.assertNotIn("(d.last_checked_utc||", page)


if __name__ == '__main__':
    unittest.main()
