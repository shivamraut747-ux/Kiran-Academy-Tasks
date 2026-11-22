from datetime import date

from rpms.exception.exceptions import (
    CandidateNotFoundError, ValidationError, DuplicateRecordError
)
from rpms.util.validation import (
    is_valid_email,
    is_valid_mobile,
    is_valid_percentage,
    is_valid_backlog_count,
    is_valid_year
)


class CandidateService:

    # statuses a user may set on the update screen (PLACED is set by the placement process)
    EDITABLE_STATUSES = ("ACTIVE", "INACTIVE", "ON_HOLD")

    def __init__(self, candidate_dao):
        self.candidate_dao = candidate_dao

    # ---------- rules used by both add and update ----------
    def _validate(self, candidate):
        if not candidate.full_name or not candidate.full_name.strip():
            raise ValidationError("Please enter candidate name.")
        if not is_valid_email(candidate.email):
            raise ValidationError("Enter a valid email address.")
        if not is_valid_mobile(candidate.mobile):
            raise ValidationError("Mobile number must contain 10 digits.")
        if not candidate.qualification or not candidate.qualification.strip():
            raise ValidationError("Please enter qualification.")
        if not is_valid_year(candidate.passing_year):
            raise ValidationError("Enter a valid passing year (for example 2025).")
        if not is_valid_percentage(candidate.percentage):
            raise ValidationError("Percentage must be between 0 and 100.")
        if not is_valid_backlog_count(candidate.backlog_count):
            raise ValidationError("Backlog count cannot be negative.")
        if not candidate.primary_technology:
            raise ValidationError("Please select primary technology.")

    def _check_duplicates(self, candidate):
        """Email and mobile must be unique. When updating, ignore the candidate itself."""
        same_email = self.candidate_dao.find_by_email(candidate.email)
        if same_email and same_email.candidate_id != candidate.candidate_id:
            raise DuplicateRecordError("Duplicate email: another candidate already uses it.")
        same_mobile = self.candidate_dao.find_by_mobile(candidate.mobile)
        if same_mobile and same_mobile.candidate_id != candidate.candidate_id:
            raise DuplicateRecordError("Duplicate mobile: another candidate already uses it.")

    def _next_code(self):
        """Creates codes like CAN-2026-0021."""
        prefix = f"CAN-{date.today().year}-"
        return f"{prefix}{self.candidate_dao.last_code_number(prefix) + 1:04d}"

    # ---------- operations ----------
    def add_candidate(self, candidate):
        self._validate(candidate)
        self._check_duplicates(candidate)
        if not candidate.candidate_code:
            candidate.candidate_code = self._next_code()
        return self.candidate_dao.save(candidate)

    def update_candidate(self, candidate):
        self.get_candidate(candidate.candidate_id)          # must exist
        self._validate(candidate)
        if candidate.profile_status not in self.EDITABLE_STATUSES:
            raise ValidationError("Status must be ACTIVE, INACTIVE or ON_HOLD.")
        self._check_duplicates(candidate)
        self.candidate_dao.update(candidate)

    def get_candidate(self, candidate_id):
        candidate = self.candidate_dao.find_by_id(candidate_id)
        if not candidate:
            raise CandidateNotFoundError(f"Candidate ID {candidate_id} not found")
        return candidate

    def get_all_candidates(self):
        return self.candidate_dao.find_all()

    def search_candidates(self, filters):
        # drop empty filters so only filled boxes are used
        clean = {k: v for k, v in filters.items() if v not in (None, "")}
        return self.candidate_dao.search(clean)

    def deactivate_candidate(self, candidate_id):
        """Soft delete: history must be kept, so we only change the status."""
        candidate = self.get_candidate(candidate_id)
        if candidate.profile_status == "INACTIVE":
            raise ValidationError("Candidate is already INACTIVE.")
        self.candidate_dao.update_profile_status(candidate_id, "INACTIVE")
        return candidate
