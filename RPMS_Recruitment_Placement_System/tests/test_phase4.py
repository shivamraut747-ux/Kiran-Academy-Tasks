"""
Phase 4 tests: interviews, feedback, offers, placements, transactions.
Run:  python -m unittest tests.test_phase4 -v
Needs MySQL + sql/rpms_full_setup.sql loaded. Creates its own test rows and deletes them.
"""
import unittest
from datetime import date, timedelta

from rpms.exception.exceptions import (
    ValidationError, InvalidStatusTransitionError, DuplicatePlacementError
)
from rpms.util.db_connection import execute, fetch_one
from rpms.util.session import set_current_user
from rpms.model.user import User
from rpms.dao.candidate_dao import CandidateDAO
from rpms.dao.job_dao import JobDAO
from rpms.dao.application_dao import ApplicationDAO
from rpms.dao.application_history_dao import ApplicationHistoryDAO
from rpms.dao.interview_dao import InterviewDAO
from rpms.dao.offer_dao import OfferDAO
from rpms.dao.placement_dao import PlacementDAO
from rpms.service.eligibility_service import EligibilityService
from rpms.service.application_service import ApplicationService
from rpms.service.interview_service import InterviewService
from rpms.service.offer_service import OfferService
from rpms.service.placement_service import PlacementService
from rpms.service.transaction_demo import rollback_demo


def build(history_dao=None):
    app_svc = ApplicationService(CandidateDAO(), JobDAO(), ApplicationDAO(), EligibilityService(),
                                 history_dao or ApplicationHistoryDAO())
    return (app_svc,
            InterviewService(InterviewDAO(), ApplicationDAO(), app_svc),
            OfferService(OfferDAO(), ApplicationDAO(), PlacementDAO(), app_svc),
            PlacementService(PlacementDAO(), OfferDAO(), app_svc))


class Phase4Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        set_current_user(User(user_id=2, username="amit.recruiter", full_name="Amit"))
        company = fetch_one("SELECT company_id FROM companies ORDER BY company_id LIMIT 1")["company_id"]
        today = date.today()
        cls.job_id = execute(
            "INSERT INTO jobs (job_code,company_id,job_title,location,openings,min_percentage,"
            "min_passing_year,max_passing_year,max_backlogs,posted_date,application_deadline,status,created_by)"
            " VALUES ('JOB-TEST-P4',%s,'P4 Test Job','Pune',5,60,2020,2030,0,%s,%s,'OPEN',2)",
            (company, today, today + timedelta(days=30)))
        cls.cands = []
        cls.app, cls.iv, cls.offer, cls.pl = build()

    @classmethod
    def tearDownClass(cls):
        for c in cls.cands:
            ids = "(SELECT application_id FROM applications WHERE candidate_id=%s)"
            execute("DELETE FROM placements WHERE candidate_id=%s", (c,))
            execute(f"DELETE FROM offers WHERE application_id IN {ids}", (c,))
            execute(f"DELETE FROM interview_feedback WHERE interview_id IN "
                    f"(SELECT interview_id FROM interview_rounds WHERE application_id IN {ids})", (c,))
            execute(f"DELETE FROM interview_rounds WHERE application_id IN {ids}", (c,))
            execute(f"DELETE FROM application_history WHERE application_id IN {ids}", (c,))
            execute("DELETE FROM applications WHERE candidate_id=%s", (c,))
            execute("DELETE FROM candidates WHERE candidate_id=%s", (c,))
        execute("DELETE FROM jobs WHERE job_id=%s", (cls.job_id,))

    def new_candidate(self, n):
        cid = execute(
            "INSERT INTO candidates (candidate_code,full_name,email,mobile,qualification,passing_year,"
            "percentage,backlog_count,primary_technology) VALUES (%s,%s,%s,%s,'BE',2025,80,0,'Java')",
            (f"CAN-TEST-P4{n}", f"P4 Tester {n}", f"p4.tester{n}@example.com", f"90000010{n:02d}"))
        self.cands.append(cid)
        return cid

    def app_status(self, app_id):
        return fetch_one("SELECT application_status AS s FROM applications WHERE application_id=%s", (app_id,))["s"]

    def to_selected(self, cid):
        app_id = self.app.apply_for_job(cid, self.job_id)
        self.app.shortlist(app_id)
        iid = self.iv.schedule(app_id, "TECHNICAL", date.today(), "10:00:00", "ONLINE", "Tester", None)
        self.iv.add_feedback(iid, 4, 4, 4, 4, "SELECTED", "Good")
        return app_id, iid

    def test_interview_rules(self):
        app_id = self.app.apply_for_job(self.new_candidate(1), self.job_id)
        with self.assertRaises(ValidationError):                 # not shortlisted yet
            self.iv.schedule(app_id, "TECHNICAL", date.today(), None, "ONLINE")
        self.app.shortlist(app_id)
        with self.assertRaises(ValidationError):                 # date in the past
            self.iv.schedule(app_id, "TECHNICAL", date.today() - timedelta(days=1), None, "ONLINE")
        iid = self.iv.schedule(app_id, "TECHNICAL", date.today(), "10:00:00", "ONLINE")
        self.assertEqual(self.app_status(app_id), "INTERVIEW_SCHEDULED")
        with self.assertRaises(ValidationError):                 # round 1 still open
            self.iv.schedule(app_id, "HR", date.today(), None, "ONLINE")
        self.iv.reschedule(iid, date.today() + timedelta(days=2), "11:00:00")
        self.assertEqual(fetch_one("SELECT status FROM interview_rounds WHERE interview_id=%s", (iid,))["status"],
                         "RESCHEDULED")
        self.iv.mark_no_show(iid)
        iid2 = self.iv.schedule(app_id, "HR", date.today(), None, "ONLINE")      # round 2 after no-show
        self.assertEqual(fetch_one("SELECT round_number AS r FROM interview_rounds WHERE interview_id=%s",
                                   (iid2,))["r"], 2)
        with self.assertRaises(ValidationError):                 # rating out of range
            self.iv.add_feedback(iid2, 9, None, None, None, "SELECTED")
        self.iv.add_feedback(iid2, 3, 3, 3, 3, "NEXT_ROUND")
        self.assertEqual(self.app_status(app_id), "INTERVIEWED")

    def test_full_placement_flow(self):
        cid = self.new_candidate(2)
        app_id, _ = self.to_selected(cid)
        self.assertEqual(self.app_status(app_id), "SELECTED")
        offer_id = self.offer.create_offer(app_id, "Developer", 5.0, date.today(), None)
        self.assertEqual(self.app_status(app_id), "OFFERED")
        with self.assertRaises(ValidationError):                 # offer not accepted yet
            self.pl.confirm_joining(offer_id, "JOINED", date.today())
        self.offer.update_status(offer_id, "ACCEPTED")
        with self.assertRaises(InvalidStatusTransitionError):    # ACCEPTED -> REJECTED not allowed
            self.offer.update_status(offer_id, "REJECTED")
        pid = self.pl.confirm_joining(offer_id, "JOINED", date.today())
        self.assertEqual(self.app_status(app_id), "JOINED")
        self.assertEqual(fetch_one("SELECT placement_status AS s FROM candidates WHERE candidate_id=%s",
                                   (cid,))["s"], "PLACED")
        with self.assertRaises(DuplicatePlacementError):
            self.pl.confirm_joining(offer_id, "JOINED", date.today())
        hist = [h["new_status"] for h in self.app.get_history(app_id)]
        self.assertEqual(hist, ["APPLIED", "SHORTLISTED", "INTERVIEW_SCHEDULED", "INTERVIEWED",
                                "SELECTED", "OFFERED", "JOINED"])
        self.assertTrue(any(r["placement_id"] == pid for r in self.pl.search("JOINED")))

    def test_offer_rejected_closes_application(self):
        app_id, _ = self.to_selected(self.new_candidate(3))
        offer_id = self.offer.create_offer(app_id, "Developer", 4.0, date.today(), None)
        self.offer.update_status(offer_id, "REJECTED", "Better offer elsewhere")
        self.assertEqual(self.app_status(app_id), "REJECTED")

    def test_rollback_on_joining_failure(self):
        """History insert fails during joining -> placement and PLACED flag are rolled back."""
        cid = self.new_candidate(4)
        app_id, _ = self.to_selected(cid)
        offer_id = self.offer.create_offer(app_id, "Developer", 4.0, date.today(), None)
        self.offer.update_status(offer_id, "ACCEPTED")

        class BrokenHistory(ApplicationHistoryDAO):
            def add(self, *a, **k):
                raise RuntimeError("simulated failure")

        _, _, _, broken_pl = build(BrokenHistory())
        with self.assertRaises(RuntimeError):
            broken_pl.confirm_joining(offer_id, "JOINED", date.today())
        self.assertIsNone(fetch_one("SELECT 1 AS x FROM placements WHERE offer_id=%s", (offer_id,)))
        self.assertEqual(fetch_one("SELECT placement_status AS s FROM candidates WHERE candidate_id=%s",
                                   (cid,))["s"], "NOT_PLACED")
        self.assertEqual(self.app_status(app_id), "OFFERED")

    def test_rollback_demo(self):
        lines = rollback_demo()
        self.assertIn("unchanged", lines[-1])
        self.assertEqual(fetch_one("SELECT COUNT(*) AS n FROM candidates WHERE college='ROLLBACK DEMO'")["n"], 0)


if __name__ == "__main__":
    unittest.main()
