from datetime import date

from mysql.connector import IntegrityError

from rpms.exception.exceptions import (
    ApplicationNotFoundError, InterviewNotFoundError, DuplicateInterviewRoundError,
    DuplicateFeedbackError, ValidationError
)
from rpms.util.db_connection import transaction
from rpms.util.session import get_current_user_id


class InterviewService:
    """Schedule / reschedule / feedback / no-show. Multi-table steps run in ONE transaction."""

    ROUND_TYPES = ("APTITUDE", "TECHNICAL", "MANAGERIAL", "HR")
    MODES = ("ONLINE", "OFFLINE", "TELEPHONIC")
    RECOMMENDATIONS = ("NEXT_ROUND", "SELECTED", "REJECTED", "ON_HOLD")

    def __init__(self, interview_dao, application_dao, application_service):
        self.interview_dao = interview_dao
        self.application_dao = application_dao
        self.application_service = application_service

    @staticmethod
    def _user_id():
        uid = get_current_user_id()
        if uid is None:
            raise ValidationError("Please log in first.")
        return uid

    @staticmethod
    def _check_date(d):
        if d is None:
            raise ValidationError("Interview date is required.")
        if d < date.today():
            raise ValidationError("Interview date cannot be in the past.")

    # ---------- schedule ----------
    def schedule(self, application_id, round_type, scheduled_date, scheduled_time,
                 mode, interviewer=None, location=None):
        self._user_id()
        if round_type not in self.ROUND_TYPES:
            raise ValidationError("Round must be one of: " + ", ".join(self.ROUND_TYPES))
        if mode not in self.MODES:
            raise ValidationError("Mode must be one of: " + ", ".join(self.MODES))
        self._check_date(scheduled_date)
        try:
            with transaction() as con:
                app = self.application_dao.find_by_id(application_id, con, lock=True)
                if not app:
                    raise ApplicationNotFoundError("Application not found")
                status = app["application_status"]
                if status == "INTERVIEW_SCHEDULED":
                    if self.interview_dao.open_round_exists(application_id, con):
                        raise ValidationError("A previous round is still open. Complete it first.")
                elif status not in ("SHORTLISTED", "INTERVIEWED"):
                    raise ValidationError(
                        f"Cannot schedule interview: application is {status} "
                        "(must be SHORTLISTED or INTERVIEWED).")
                round_no = self.interview_dao.max_round(application_id, con) + 1
                interview_id = self.interview_dao.insert(
                    application_id, round_no, round_type, scheduled_date, scheduled_time,
                    mode, interviewer, location, con)
                if status != "INTERVIEW_SCHEDULED":
                    self.application_service.change_status(
                        application_id, "INTERVIEW_SCHEDULED",
                        f"Round {round_no} ({round_type}) scheduled", con)
            return interview_id
        except IntegrityError as exc:                       # UNIQUE(application_id, round_number)
            raise DuplicateInterviewRoundError("This interview round already exists.") from exc

    # ---------- reschedule ----------
    def reschedule(self, interview_id, new_date, new_time):
        self._check_date(new_date)
        with transaction() as con:
            iv = self.interview_dao.find_by_id(interview_id, con, lock=True)
            if not iv:
                raise InterviewNotFoundError("Interview not found")
            if iv["status"] not in ("SCHEDULED", "RESCHEDULED"):
                raise ValidationError(f"Only open interviews can be rescheduled (status is {iv['status']}).")
            self.interview_dao.reschedule(interview_id, new_date, new_time, con)

    # ---------- feedback (interview completion) ----------
    def add_feedback(self, interview_id, technical, communication, problem_solving,
                     overall, recommendation, remarks=None):
        user_id = self._user_id()
        if recommendation not in self.RECOMMENDATIONS:
            raise ValidationError("Result must be one of: " + ", ".join(self.RECOMMENDATIONS))
        for r in (technical, communication, problem_solving, overall):
            if r is not None and not (0 <= r <= 5):
                raise ValidationError("Ratings must be between 0 and 5.")
        with transaction() as con:
            iv = self.interview_dao.find_by_id(interview_id, con, lock=True)
            if not iv:
                raise InterviewNotFoundError("Interview not found")
            if iv["status"] not in ("SCHEDULED", "RESCHEDULED"):
                raise ValidationError(f"Feedback needs an open interview (status is {iv['status']}).")
            if self.interview_dao.feedback_exists(interview_id, con):
                raise DuplicateFeedbackError("Feedback already exists for this interview.")
            # 1) save feedback  2) complete interview  3) move the application
            self.interview_dao.insert_feedback(interview_id, technical, communication,
                                               problem_solving, overall, recommendation,
                                               remarks, user_id, con)
            self.interview_dao.set_status(interview_id, "COMPLETED", con)
            app_id = iv["application_id"]
            note = f"Round {iv['round_number']} result: {recommendation}"
            self.application_service.change_status(app_id, "INTERVIEWED", note, con)
            if recommendation == "SELECTED":
                self.application_service.change_status(app_id, "SELECTED", "Selected after interview", con)
            elif recommendation == "REJECTED":
                self.application_service.change_status(app_id, "REJECTED", remarks or "Rejected after interview", con)
            # NEXT_ROUND / ON_HOLD: application stays INTERVIEWED

    # ---------- no show ----------
    def mark_no_show(self, interview_id):
        with transaction() as con:
            iv = self.interview_dao.find_by_id(interview_id, con, lock=True)
            if not iv:
                raise InterviewNotFoundError("Interview not found")
            if iv["status"] not in ("SCHEDULED", "RESCHEDULED"):
                raise ValidationError(f"Only open interviews can be marked NO_SHOW (status is {iv['status']}).")
            self.interview_dao.set_status(interview_id, "NO_SHOW", con)
        # The application stays INTERVIEW_SCHEDULED; a new round can be scheduled, or reject it.

    def search(self, **filters):
        return self.interview_dao.search(**filters)
