"""
Phase 5 tests: every report runs and the numbers agree with each other.
Run:  python -m unittest tests.test_phase5 -v     (needs MySQL + sql/rpms_full_setup.sql)
"""
import unittest

from rpms.service.report_service import ReportService, REPORTS
from rpms.util.db_connection import fetch_one


class ReportTest(unittest.TestCase):
    svc = ReportService()

    def rows(self, key):
        return self.svc.run(key)[1]

    def test_all_reports_run(self):
        self.assertEqual(len(REPORTS), 13)
        for key in REPORTS:
            title, rows = self.svc.run(key)
            self.assertIsInstance(rows, list, title)

    def test_candidates_by_technology_total(self):
        total = sum(r["total_candidates"] for r in self.rows("candidates_by_technology"))
        self.assertEqual(total, fetch_one("SELECT COUNT(*) AS n FROM candidates")["n"])

    def test_applications_by_status_total(self):
        total = sum(r["total"] for r in self.rows("applications_by_status"))
        self.assertEqual(total, fetch_one("SELECT COUNT(*) AS n FROM applications")["n"])

    def test_placement_reports_agree(self):
        joined = fetch_one("SELECT COUNT(*) AS n FROM placements WHERE joining_status='JOINED'")["n"]
        self.assertEqual(sum(r["placed_count"] for r in self.rows("company_wise_placements")), joined)
        self.assertEqual(sum(r["placed_count"] for r in self.rows("technology_wise_placements")), joined)
        self.assertEqual(len(self.rows("placed_candidates")), joined)

    def test_placed_plus_unplaced_is_all_candidates(self):
        placed = fetch_one("SELECT COUNT(*) AS n FROM candidates WHERE placement_status='PLACED'")["n"]
        unplaced = len(self.rows("unplaced_candidates"))
        self.assertEqual(placed + unplaced, fetch_one("SELECT COUNT(*) AS n FROM candidates")["n"])

    def test_funnel_never_grows(self):
        counts = [r["applications"] for r in self.rows("recruitment_funnel")]
        self.assertEqual(len(counts), 7)
        self.assertGreaterEqual(counts[0], counts[-1])

    def test_conversion(self):
        row = self.rows("offer_to_join_conversion")[0]
        self.assertGreaterEqual(row["total_offers"], 8)
        self.assertLessEqual(row["joined"], row["total_offers"])

    def test_open_job_reports_match(self):
        self.assertEqual(len(self.rows("open_jobs")), len(self.rows("job_aging")))
        self.assertEqual(sum(r["open_jobs"] for r in self.rows("open_jobs_by_company")), len(self.rows("open_jobs")))

    def test_pending_interviews_only_open_status(self):
        for r in self.rows("pending_interviews"):
            self.assertIn(r["status"], ("SCHEDULED", "RESCHEDULED"))


if __name__ == "__main__":
    unittest.main()
