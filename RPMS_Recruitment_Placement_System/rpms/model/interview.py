from dataclasses import dataclass

@dataclass
class Interview:
    interview_id: int | None = None
    application_id: int = 0
    round_number: int = 1
    round_type: str = ""
    mode: str = ""
    status: str = "SCHEDULED"
