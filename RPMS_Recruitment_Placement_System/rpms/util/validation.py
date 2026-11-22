import re

def is_valid_email(email: str) -> bool:
    return bool(email and re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))

def is_valid_mobile(mobile: str) -> bool:
    return bool(mobile and re.fullmatch(r"\d{10}", mobile))

def is_valid_percentage(value: float) -> bool:
    return 0 <= value <= 100

def is_valid_backlog_count(value: int) -> bool:
    return value >= 0


# ---------- Added in Phase 2 ----------
def is_valid_year(value: int) -> bool:
    return value is not None and 1990 <= value <= 2100


def is_valid_optional_mobile(mobile: str) -> bool:
    """Empty is allowed; if given it must be 10 digits."""
    return (not mobile) or bool(re.fullmatch(r"\d{10}", mobile))
