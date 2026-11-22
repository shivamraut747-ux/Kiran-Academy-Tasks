class CandidateNotFoundError(Exception):
    pass

class JobNotFoundError(Exception):
    pass

class DuplicateApplicationError(Exception):
    pass

class CandidateNotEligibleError(Exception):
    pass


# ---------- Added in Phase 2 ----------
class ValidationError(ValueError):
    """Raised when user input breaks a business rule (bad email, wrong date...)."""
    pass


class DuplicateRecordError(ValueError):
    """Raised when a unique value (email, mobile) already exists."""
    pass


class CompanyNotFoundError(Exception):
    pass


class LoginError(Exception):
    pass


# ---------- Added in Phase 3 ----------
class ApplicationNotFoundError(Exception):
    pass


class InvalidStatusTransitionError(Exception):
    """Raised when someone tries a workflow jump that is not allowed (APPLIED -> JOINED)."""
    pass


# ---------- Added in Phase 4 ----------
class InterviewNotFoundError(Exception):
    pass


class DuplicateInterviewRoundError(Exception):
    pass


class DuplicateFeedbackError(Exception):
    pass


class OfferNotFoundError(Exception):
    pass


class DuplicateOfferError(Exception):
    pass


class PlacementNotFoundError(Exception):
    pass


class DuplicatePlacementError(Exception):
    pass
