"""Remembers who is logged in (used for changed_by, created_by, recruiter)."""

_current_user = None


def set_current_user(user):
    global _current_user
    _current_user = user


def get_current_user():
    return _current_user


def get_current_user_id():
    return _current_user.user_id if _current_user else None
