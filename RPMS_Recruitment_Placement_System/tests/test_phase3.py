"""
Phase 3 tests: workflow rules, application history, transactions.
Run:  python -m unittest tests.test_phase3 -v
Part A needs no database. Part B needs MySQL + sql/rpms_full_setup.sql loaded.
Part B creates its own candidate/job and deletes them at the end.
"""
import unittest
from datetime import date, timedelta

from rpms.util.workflow import check_transition
from rpms.exception.exceptions import (
    InvalidStatusTransitionError, DuplicateApplicationError, ApplicationNotFoundError,
    ValidationError, CandidateNotEligibleError
)


class WorkflowRulesTest(unittest.TestCase):          # ---- Part A: no database ----
    def test_valid_steps(self):
        for old, new in [("APPLIED", "SHORTLISTED"), ("SHORTLISTED", "INTERVIEW_SCHEDULED"),
                         ("INTERVIEWED", "SELECTED"), ("SELECTED", "OFFERED"),
                         ("OFFERED", "JOINED"), ("APPLIED", "REJECTED")]:
            check_transition(old, new)               # must not raise

    def test_invalid_jumps_blocked(self):
        for old, new in [("APPLIED", "JOINED"), ("APPLIED", "SELECTED"),
                         ("SHORTLISTED", "OFFERED"), ("REJECTED", "SHORTLISTED"),
                         ("JOINED", "APPLIED")]:
            with self.assertRaises(InvalidStatusTransitionError):
                check_transition(old, new)

    def test_unknown_status(self):
        with self.assertRaises(InvalidStatusTransitionError):
            check_transition("APPLIED", "HIRED")


try:
    from rpms.util.db_connection import execute, fetch_one, fetch_all, get_connection
    from rpms.util.session import set_current_user
    from rpms.model.user import User
    from rpms.dao.candidate_dao import CandidateDAO
    from rpms.dao.job_dao import JobDAO
    from rpms.dao.application_dao import ApplicationDAO
    from rpms.dao.application_history_dao import ApplicationHistoryDAO
    from rpms.service.eligibility_service import EligibilityService
    from rpms.service.application_service import ApplicationService
    get_connection().close()
    DB_OK = True
except Exception:
    DB_OK = False


@unittest.skipUnless(DB_OK, "MySQL not reachable - skipping database tests")
class ApplicationWorkflowDBTest(unittest.TestCase):  # ---- Part B: database ----
    @classmethod
    def setUpClass(cls):
        set_current_user(User(user_id=2, username="amit.recruiter", full_name="Amit"))
        cls.cand_id = execute(
            "INSERT INTO candidates (candidate_code,full_name,email,mobile,qualification,"
            "passing_year,percentage,backlog_count,primary_technology) VALUES "
            "('CAN-TEST-P3','Phase3 Tester','p3.tester@example.com','7770000003','BE',2025,80,0,'Java')")
        company = fetch_one("SELECT company_id FROM companies ORDER BY company_id LIMIT 1")["company_id"]
        today = date.today()
        cls.job_id = execute(
            "INSERT INTO jobs (job_code,company_id,job_title,location,openings,min_percentage,"
            "min_passing_year,max_passing_year,max_backlogs,posted_date,application_deadline,status,created_by)"
            " VALUES ('JOB-TEST-P3',%s,'P3 Test Job','Pune',1,60,2020,2030,0,%s,%s,'OPEN',2)",
            (company, today, today + timedelta(days=30)))
        cls.svc = ApplicationService(CandidateDAO(), JobDAO(), ApplicationDAO(),
                                     EligibilityService(), ApplicationHistoryDAO())

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM application_history WHERE application_id IN "
                "(SELECT application_id FROM applications WHERE candidate_id=%s)", (cls.cand_id,))
        execute("DELETE FROM applications WHERE candidate_id=%s", (cls.cand_id,))
        execute("DELETE FROM jobs WHERE job_id=%s", (cls.job_id,))
        execute("DELETE FROM candidates WHERE candidate_id=%s", (cls.cand_id,))

    def status(self, app_id):
        return fetch_one("SELECT application_status AS s FROM applications "
                         "WHERE application_id=%s", (app_id,))["s"]

    def test_full_flow(self):
        app_id = self.svc.apply_for_job(self.cand_id, self.job_id)
        self.assertEqual(self.status(app_id), "APPLIED")
        with self.assertRaises(DuplicateApplicationError):          # duplicate blocked
            self.svc.apply_for_job(self.cand_id, self.job_id)
        with self.assertRaises(InvalidStatusTransitionError):       # jump blocked
            self.svc.change_status(app_id, "JOINED", "illegal")
        self.assertEqual(self.status(app_id), "APPLIED")
        self.svc.shortlist(app_id)
        self.assertEqual(self.status(app_id), "SHORTLISTED")
        with self.assertRaises(ValidationError):                    # reason is required
            self.svc.reject(app_id, "  ")
        self.svc.reject(app_id, "Not a fit")
        self.assertEqual(self.status(app_id), "REJECTED")
        with self.assertRaises(InvalidStatusTransitionError):       # REJECTED is final
            self.svc.shortlist(app_id)
        history = self.svc.get_history(app_id)
        self.assertEqual([(h["old_status"], h["new_status"]) for h in history],
                         [(None, "APPLIED"), ("APPLIED", "SHORTLISTED"), ("SHORTLISTED", "REJECTED")])
        self.assertTrue(any(r["application_id"] == app_id for r in self.svc.search(status="REJECTED")))

    def test_rollback_when_history_fails(self):
        """If the history insert fails, the status update is undone (transaction rollback)."""
        cand2 = execute(
            "INSERT INTO candidates (candidate_code,full_name,email,mobile,qualification,"
            "passing_year,percentage,backlog_count,primary_technology) VALUES "
            "('CAN-TEST-P3B','Rollback Tester','p3.rollback@example.com','7770000004','BE',2025,80,0,'Java')")
        try:
            app_id = self.svc.apply_for_job(cand2, self.job_id)

            class BrokenHistory(ApplicationHistoryDAO):
                def add(self, *args, **kwargs):
                    raise RuntimeError("simulated failure")

            broken = ApplicationService(CandidateDAO(), JobDAO(), ApplicationDAO(),
                                        EligibilityService(), BrokenHistory())
            with self.assertRaises(RuntimeError):
                broken.shortlist(app_id)
            self.assertEqual(self.status(app_id), "APPLIED")        # unchanged = rolled back
        finally:
            execute("DELETE FROM application_history WHERE application_id IN "
                    "(SELECT application_id FROM applications WHERE candidate_id=%s)", (cand2,))
            execute("DELETE FROM applications WHERE candidate_id=%s", (cand2,))
            execute("DELETE FROM candidates WHERE candidate_id=%s", (cand2,))

    def test_not_found(self):
        with self.assertRaises(ApplicationNotFoundError):
            self.svc.shortlist(99999999)


if __name__ == "__main__":
    unittest.main()
