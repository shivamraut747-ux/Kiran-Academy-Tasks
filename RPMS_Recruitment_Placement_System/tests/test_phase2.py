"""
Phase 2 tests: Candidate, Company, Job modules, login and the transaction helper.
Run from the project folder:   python -m unittest tests.test_phase2 -v
Needs MySQL running with the sample data loaded (sql/rpms_full_setup.sql).
Each test removes the rows it created, so the database stays as it was.
"""
import unittest
from datetime import date, timedelta

from rpms.dao.candidate_dao import CandidateDAO
from rpms.dao.company_dao import CompanyDAO
from rpms.dao.job_dao import JobDAO
from rpms.dao.skill_dao import SkillDAO
from rpms.dao.user_dao import UserDAO
from rpms.model.candidate import Candidate
from rpms.model.company import Company
from rpms.model.job import Job
from rpms.service.candidate_service import CandidateService
from rpms.service.company_service import CompanyService
from rpms.service.job_service import JobService
from rpms.service.user_service import UserService
from rpms.exception.exceptions import (
    ValidationError, DuplicateRecordError, CandidateNotFoundError,
    CompanyNotFoundError, JobNotFoundError, LoginError
)
from rpms.util.db_connection import execute, fetch_one


def new_candidate(**changes):
    data = dict(full_name="Test Student", email="test.student@example.com", mobile="9876543210",
                qualification="BE", passing_year=2025, percentage=70.0, backlog_count=0,
                primary_technology="Java")
    data.update(changes)
    return Candidate(**data)


def new_company(**changes):
    data = dict(company_name="Test Corp", industry="IT", location="Pune", hr_name="Test HR",
                hr_email="hr@testcorp.com", company_type="STARTUP")
    data.update(changes)
    return Company(**data)


def new_job(company_id=1, **changes):
    today = date.today()
    data = dict(company_id=company_id, job_title="Test Developer", location="Pune", openings=3,
                min_package_lpa=3.0, max_package_lpa=5.0, min_percentage=60, max_backlogs=0,
                posted_date=today, application_deadline=today + timedelta(days=30))
    data.update(changes)
    return Job(**data)


class Phase2Base(unittest.TestCase):
    def setUp(self):
        self.candidate_dao, self.company_dao = CandidateDAO(), CompanyDAO()
        self.job_dao, self.skill_dao = JobDAO(), SkillDAO()
        self.candidates = CandidateService(self.candidate_dao)
        self.companies = CompanyService(self.company_dao)
        self.jobs = JobService(self.job_dao, self.company_dao, self.skill_dao)

    def tearDown(self):
        # remove only rows created by tests
        execute("DELETE FROM job_skills WHERE job_id IN (SELECT job_id FROM jobs WHERE job_title LIKE 'Test %')")
        execute("DELETE FROM jobs WHERE job_title LIKE 'Test %'")
        execute("DELETE FROM companies WHERE company_name LIKE 'Test %'")
        execute("DELETE FROM candidates WHERE email LIKE 'test.%@example.com'")


class CandidateTests(Phase2Base):
    def test_add_generates_code_and_saves(self):
        before = fetch_one("SELECT COUNT(*) n FROM candidates")["n"]
        cid = self.candidates.add_candidate(new_candidate())
        saved = self.candidates.get_candidate(cid)
        self.assertRegex(saved.candidate_code, r"^CAN-\d{4}-\d{4}$")
        self.assertEqual(saved.profile_status, "ACTIVE")
        self.assertEqual(fetch_one("SELECT COUNT(*) n FROM candidates")["n"], before + 1)

    def test_validation_messages(self):
        cases = [
            (dict(full_name=" "), "Please enter candidate name."),
            (dict(email="bad-email"), "Enter a valid email address."),
            (dict(mobile="12345"), "Mobile number must contain 10 digits."),
            (dict(percentage=101), "Percentage must be between 0 and 100."),
            (dict(backlog_count=-1), "Backlog count cannot be negative."),
        ]
        for changes, message in cases:
            with self.subTest(message=message):
                with self.assertRaises(ValidationError) as ctx:
                    self.candidates.add_candidate(new_candidate(**changes))
                self.assertEqual(str(ctx.exception), message)

    def test_duplicate_email_and_mobile_blocked(self):
        self.candidates.add_candidate(new_candidate())
        with self.assertRaises(DuplicateRecordError):
            self.candidates.add_candidate(new_candidate(mobile="9876500000"))      # same email
        with self.assertRaises(DuplicateRecordError):
            self.candidates.add_candidate(new_candidate(email="test.other@example.com"))  # same mobile

    def test_update_keeps_own_email_but_blocks_anothers(self):
        cid = self.candidates.add_candidate(new_candidate())
        other = self.candidates.add_candidate(new_candidate(email="test.two@example.com", mobile="9876500001"))
        mine = self.candidates.get_candidate(cid)
        mine.percentage = 75.5
        self.candidates.update_candidate(mine)                                   # own email/mobile: allowed
        self.assertEqual(self.candidates.get_candidate(cid).percentage, 75.5)
        mine.email = "test.two@example.com"
        with self.assertRaises(DuplicateRecordError):
            self.candidates.update_candidate(mine)

    def test_update_unknown_candidate(self):
        with self.assertRaises(CandidateNotFoundError):
            self.candidates.update_candidate(new_candidate(candidate_id=999999))

    def test_search_filters(self):
        self.assertTrue(all(c.primary_technology == "Python"
                            for c in self.candidates.search_candidates({"technology": "Python"})))
        placed = self.candidates.search_candidates({"status": "PLACED"})
        self.assertTrue(placed and all(c.placement_status == "PLACED" for c in placed))
        by_name = self.candidates.search_candidates({"full_name": "rahul"})
        self.assertEqual([c.candidate_code for c in by_name], ["CAN-2026-0001"])
        self.assertGreaterEqual(len(self.candidates.search_candidates({})), 30)       # no filter = all

    def test_deactivate_is_soft_and_not_repeatable(self):
        cid = self.candidates.add_candidate(new_candidate())
        self.candidates.deactivate_candidate(cid)
        self.assertEqual(self.candidates.get_candidate(cid).profile_status, "INACTIVE")   # row still exists
        with self.assertRaises(ValidationError):
            self.candidates.deactivate_candidate(cid)


class CompanyTests(Phase2Base):
    def test_add_update_and_status(self):
        cid = self.companies.add_company(new_company())
        company = self.companies.get_company(cid)
        self.assertRegex(company.company_code, r"^COM-\d{3}$")
        company.location = "Mumbai"
        self.companies.update_company(company)
        self.assertEqual(self.companies.get_company(cid).location, "Mumbai")
        self.companies.set_status(cid, "INACTIVE")
        self.assertEqual(self.companies.get_company(cid).status, "INACTIVE")
        with self.assertRaises(ValidationError):
            self.companies.set_status(cid, "INACTIVE")

    def test_validation(self):
        with self.assertRaises(ValidationError):
            self.companies.add_company(new_company(company_name=""))
        with self.assertRaises(ValidationError):
            self.companies.add_company(new_company(hr_email="nope"))
        with self.assertRaises(ValidationError):
            self.companies.add_company(new_company(hr_mobile="123"))
        with self.assertRaises(ValidationError):
            self.companies.add_company(new_company(company_type="OTHER"))

    def test_open_jobs_count_and_search(self):
        tech_nova = self.companies.get_company(1)
        self.assertEqual(tech_nova.open_jobs, fetch_one(
            "SELECT COUNT(*) n FROM jobs WHERE company_id=1 AND status='OPEN'")["n"])
        self.assertEqual(len(self.companies.search_companies({"location": "Pune"})) > 0, True)
        with self.assertRaises(CompanyNotFoundError):
            self.companies.get_company(999999)


class JobTests(Phase2Base):
    def test_create_job_with_skills(self):
        job_id, code = self.jobs.create_job(new_job(), ["Java", "SQL"], created_by=2)
        self.assertRegex(code, r"^JOB-\d{4}-\d{3}$")
        details = self.jobs.get_job_details(job_id)
        self.assertEqual(details.skills, "Java, SQL")
        self.assertEqual(details.company_name, "TechNova Solutions")
        self.assertEqual(details.status, "OPEN")

    def test_validation_messages(self):
        today = date.today()
        cases = [
            (dict(openings=0), "Number of openings must be greater than zero."),
            (dict(application_deadline=today - timedelta(days=1)), "Application deadline cannot be before posted date."),
            (dict(min_package_lpa=9.0, max_package_lpa=4.0), "Minimum package cannot exceed maximum package."),
            (dict(min_percentage=150), "Percentage must be between 0 and 100."),
        ]
        for changes, message in cases:
            with self.subTest(message=message):
                with self.assertRaises(ValidationError) as ctx:
                    self.jobs.create_job(new_job(**changes), [], created_by=2)
                self.assertEqual(str(ctx.exception), message)

    def test_unknown_skill_saves_nothing(self):
        before = fetch_one("SELECT COUNT(*) n FROM jobs")["n"]
        with self.assertRaises(ValidationError):
            self.jobs.create_job(new_job(), ["Java", "Klingon"], created_by=2)
        self.assertEqual(fetch_one("SELECT COUNT(*) n FROM jobs")["n"], before)

    def test_rollback_when_second_table_fails(self):
        """The job row is inserted first. If saving skills fails, the job must be rolled back too."""
        before = fetch_one("SELECT COUNT(*) n FROM jobs")["n"]
        def broken(*args, **kwargs):
            raise RuntimeError("simulated failure while saving skills")
        self.job_dao.replace_skills = broken
        with self.assertRaises(RuntimeError):
            self.jobs.create_job(new_job(), ["Java"], created_by=2)
        self.assertEqual(fetch_one("SELECT COUNT(*) n FROM jobs")["n"], before)

    def test_job_needs_active_company(self):
        cid = self.companies.add_company(new_company())
        self.companies.set_status(cid, "INACTIVE")
        with self.assertRaises(ValidationError):
            self.jobs.create_job(new_job(company_id=cid), [], created_by=2)
        with self.assertRaises(CompanyNotFoundError):
            self.jobs.create_job(new_job(company_id=999999), [], created_by=2)

    def test_update_replaces_skills_and_close(self):
        job_id, _ = self.jobs.create_job(new_job(), ["Java"], created_by=2)
        job = self.jobs.get_job(job_id)
        job.openings = 7
        self.jobs.update_job(job, ["Python", "MySQL"])
        details = self.jobs.get_job_details(job_id)
        self.assertEqual((details.openings, details.skills), (7, "MySQL, Python"))
        self.jobs.update_job(job, None)                                          # None = keep skills
        self.assertEqual(self.jobs.get_job_details(job_id).skills, "MySQL, Python")
        self.jobs.close_job(job_id)
        self.assertEqual(self.jobs.get_job(job_id).status, "CLOSED")
        with self.assertRaises(ValidationError):
            self.jobs.close_job(job_id)
        with self.assertRaises(JobNotFoundError):
            self.jobs.close_job(999999)

    def test_search(self):
        java_jobs = self.jobs.search_jobs({"technology": "Java"})
        self.assertTrue(java_jobs and all("Java" in j.skills for j in java_jobs))
        self.assertTrue(all(j.status == "OPEN" for j in self.jobs.get_open_jobs()))
        self.assertEqual([j.job_code for j in self.jobs.search_jobs({"job_code": "JOB-2026-001"})],
                         ["JOB-2026-001"])


class LoginTests(unittest.TestCase):
    def test_login(self):
        service = UserService(UserDAO())
        user = service.login("amit.recruiter")
        self.assertEqual((user.user_id, user.role_code), (2, "RECRUITER"))
        with self.assertRaises(LoginError):
            service.login("nobody")
        self.assertEqual(len(service.get_active_users()), 5)


if __name__ == "__main__":
    unittest.main()
