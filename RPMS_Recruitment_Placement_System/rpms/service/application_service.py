from datetime import date

from rpms.exception.exceptions import (
    CandidateNotFoundError, JobNotFoundError, DuplicateApplicationError,
    CandidateNotEligibleError, ApplicationNotFoundError, ValidationError
)
from rpms.model.application import Application
from rpms.util.db_connection import transaction
from rpms.util.session import get_current_user_id
from rpms.util.workflow import check_transition
from rpms.dao.application_history_dao import ApplicationHistoryDAO


class ApplicationService:
    """Business rules for applications: apply, verify, shortlist, reject, withdraw, history.
    Every status change = update application + insert history, inside ONE transaction."""

    def __init__(self, candidate_dao, job_dao, application_dao, eligibility_service,
                 history_dao=None):
        self.candidate_dao = candidate_dao
        self.job_dao = job_dao
        self.application_dao = application_dao
        self.eligibility_service = eligibility_service
        self.history_dao = history_dao or ApplicationHistoryDAO()

    # ---------- small helpers ----------
    @staticmethod
    def _user_id():
        user_id = get_current_user_id()
        if user_id is None:
            raise ValidationError("Please log in first (changed_by is required).")
        return user_id

    # ---------- apply ----------
    def apply_for_job(self, candidate_id: int, job_id: int) -> int:
        user_id = self._user_id()
        candidate = self.candidate_dao.find_by_id(candidate_id)
        if not candidate:
            raise CandidateNotFoundError("Candidate not found")
        job = self.job_dao.find_by_id(job_id)
        if not job:
            raise JobNotFoundError("Job not found")
        if self.application_dao.exists(candidate_id, job_id):
            raise DuplicateApplicationError("Candidate has already applied for this job")
        reasons = self.eligibility_service.get_failure_reasons(candidate, job)
        if reasons:
            raise CandidateNotEligibleError("; ".join(reasons))

        # application row + first history row are saved together (or not at all)
        with transaction() as con:
            app = Application(
                application_code=self.application_dao.next_code(date.today().year, con),
                candidate_id=candidate_id, job_id=job_id,
                eligibility_status="ELIGIBLE",
                eligibility_reason="Meets eligibility criteria",
                application_status="APPLIED")
            application_id = self.application_dao.save_tx(app, user_id, "Recruiter", con)
            self.history_dao.add(application_id, None, "APPLIED",
                                 "Application created", user_id, con)
        return application_id

    # ---------- the one place where status changes ----------
    def change_status(self, application_id, new_status, remarks=None, con=None):
        """Validate the jump, update the application, write history.
        Pass con when another service (interview/offer) wants this to be part of ITS transaction.
        Returns the old status."""
        user_id = self._user_id()
        if con is None:
            with transaction() as own_con:
                return self.change_status(application_id, new_status, remarks, own_con)
        app = self.application_dao.find_by_id(application_id, con, lock=True)
        if not app:
            raise ApplicationNotFoundError("Application not found")
        old_status = app["application_status"]
        check_transition(old_status, new_status)           # raises if jump not allowed
        self.application_dao.update_status(application_id, new_status, con)
        self.history_dao.add(application_id, old_status, new_status, remarks, user_id, con)
        return old_status

    def shortlist(self, application_id, remarks=None):
        return self.change_status(application_id, "SHORTLISTED", remarks or "Shortlisted")

    def reject(self, application_id, remarks):
        if not remarks or not remarks.strip():
            raise ValidationError("Please enter a reason for rejection.")
        return self.change_status(application_id, "REJECTED", remarks.strip())

    def withdraw(self, application_id, remarks=None):
        return self.change_status(application_id, "WITHDRAWN", remarks or "Withdrawn by candidate")

    # ---------- re-check eligibility of an existing application ----------
    def verify_eligibility(self, application_id):
        """Run the eligibility engine again. Returns (is_eligible, reasons).
        If eligible and still APPLIED, status moves to ELIGIBILITY_VERIFIED."""
        self._user_id()
        app = self.application_dao.find_by_id(application_id)
        if not app:
            raise ApplicationNotFoundError("Application not found")
        candidate = self.candidate_dao.find_by_id(app["candidate_id"])
        job = self.job_dao.find_by_id(app["job_id"])
        # The deadline only matters when applying, so it is ignored for old applications.
        reasons = [r for r in self.eligibility_service.get_failure_reasons(candidate, job)
                   if "deadline" not in r.lower()]
        with transaction() as con:
            if reasons:
                self.application_dao.update_eligibility(
                    application_id, "NOT_ELIGIBLE", "; ".join(reasons), con)
            else:
                self.application_dao.update_eligibility(
                    application_id, "ELIGIBLE", "Meets eligibility criteria", con)
                if app["application_status"] == "APPLIED":
                    self.change_status(application_id, "ELIGIBILITY_VERIFIED",
                                       "Eligibility verified", con)
        return (not reasons), reasons

    # ---------- read-only ----------
    def search(self, **filters):
        return self.application_dao.search(**filters)

    def get_history(self, application_id):
        if not self.application_dao.find_by_id(application_id):
            raise ApplicationNotFoundError("Application not found")
        return self.history_dao.find_by_application(application_id)

    def status_summary(self):
        """dict[str, int] of applications per status (pipeline summary)."""
        return {r["application_status"]: r["total"] for r in self.application_dao.count_by_status()}
