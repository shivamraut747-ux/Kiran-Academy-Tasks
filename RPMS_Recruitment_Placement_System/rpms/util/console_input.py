"""
Small helpers to read input from the console.
They keep asking until the value is valid, so menus stay short.
If a 'current' value is given (update screens), pressing Enter keeps it.
"""
from datetime import date, datetime


def _hint(current):
    return f" [{current}]" if current not in (None, "") else ""


def ask_text(label, current=None, required=False):
    while True:
        value = input(f"{label}{_hint(current)}: ").strip()
        if value == "":
            if current not in (None, ""):
                return current
            if required:
                print("  This field is required.")
                continue
            return ""
        return value


def ask_int(label, current=None, required=False):
    while True:
        value = ask_text(label, current, required)
        if value in ("", None):
            return None
        try:
            return int(value)
        except ValueError:
            print("  Please enter a whole number.")


def ask_float(label, current=None, required=False):
    while True:
        value = ask_text(label, current, required)
        if value in ("", None):
            return None
        try:
            return float(value)
        except ValueError:
            print("  Please enter a number.")


def ask_date(label, current=None, required=False):
    """Date format: YYYY-MM-DD. Returns a datetime.date (or None)."""
    while True:
        value = ask_text(f"{label} (YYYY-MM-DD)", current, required)
        if value in ("", None):
            return None
        if isinstance(value, date):
            return value
        try:
            return datetime.strptime(str(value), "%Y-%m-%d").date()
        except ValueError:
            print("  Date must look like 2026-12-31.")


def ask_choice(label, options, current=None, required=True):
    """Ask the user to type one of the options (case-insensitive)."""
    lookup = {opt.upper(): opt for opt in options}
    while True:
        value = ask_text(f"{label} ({'/'.join(options)})", current, required)
        if value == "" and not required:
            return ""
        if str(value).upper() in lookup:
            return lookup[str(value).upper()]
        print(f"  Please choose one of: {', '.join(options)}")


def ask_yes_no(label):
    return input(f"{label} (y/n): ").strip().lower() == "y"


def ask_time(label, required=False):
    """Time format HH:MM (24 hour). Returns 'HH:MM:SS' text (or None)."""
    from datetime import datetime
    while True:
        value = ask_text(f"{label} (HH:MM, 24 hour)", None, required)
        if value == "":
            return None
        try:
            return datetime.strptime(value, "%H:%M").strftime("%H:%M:%S")
        except ValueError:
            print("  Time must look like 14:30.")
