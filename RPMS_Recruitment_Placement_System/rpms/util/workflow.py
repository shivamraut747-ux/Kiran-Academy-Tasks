"""
Application workflow rules (statuses are from the Database Design PDF, section 21).

ALLOWED_TRANSITIONS says: "from this status, you may only go to these statuses".
Anything not listed is blocked, so APPLIED -> JOINED is impossible.
This file has no database code, so it is easy to test and explain.
"""
from rpms.exception.exceptions import InvalidStatusTransitionError

ALLOWED_TRANSITIONS = {
    "APPLIED":               ["ELIGIBILITY_VERIFIED", "SHORTLISTED", "REJECTED", "WITHDRAWN"],
    "ELIGIBILITY_VERIFIED":  ["SHORTLISTED", "REJECTED", "WITHDRAWN"],
    "SHORTLISTED":           ["INTERVIEW_SCHEDULED", "REJECTED", "WITHDRAWN"],
    "INTERVIEW_SCHEDULED":   ["INTERVIEWED", "REJECTED", "WITHDRAWN"],
    # INTERVIEWED -> INTERVIEW_SCHEDULED means "next interview round"
    "INTERVIEWED":           ["INTERVIEW_SCHEDULED", "SELECTED", "REJECTED", "WITHDRAWN"],
    "SELECTED":              ["OFFERED", "REJECTED", "WITHDRAWN"],
    "OFFERED":               ["JOINED", "REJECTED", "WITHDRAWN"],
    # final statuses: nothing can follow them
    "JOINED":                [],
    "REJECTED":              [],
    "WITHDRAWN":             [],
}

ALL_STATUSES = list(ALLOWED_TRANSITIONS.keys())


def check_transition(old_status, new_status):
    """Raise InvalidStatusTransitionError if old_status -> new_status is not allowed."""
    if new_status not in ALLOWED_TRANSITIONS:
        raise InvalidStatusTransitionError(f"Unknown status: {new_status}")
    if old_status not in ALLOWED_TRANSITIONS:
        raise InvalidStatusTransitionError(f"Unknown current status: {old_status}")
    if new_status not in ALLOWED_TRANSITIONS[old_status]:
        allowed = ", ".join(ALLOWED_TRANSITIONS[old_status]) or "none (final status)"
        raise InvalidStatusTransitionError(
            f"Invalid status change {old_status} -> {new_status}. Allowed next status: {allowed}"
        )
