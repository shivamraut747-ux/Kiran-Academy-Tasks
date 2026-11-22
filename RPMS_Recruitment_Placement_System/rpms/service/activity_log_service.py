from datetime import datetime
from pathlib import Path


class ActivityLogService:

    # activity_log.txt is always created in the project root folder,
    # no matter from which folder the program is started.
    LOG_FILE = Path(__file__).resolve().parents[2] / "activity_log.txt"

    def log(self, message: str):
        with open(self.LOG_FILE, "a", encoding="utf-8") as file:
            file.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} | {message}\n")
