from dataclasses import dataclass

@dataclass
class User:
    user_id: int | None = None
    username: str = ""
    full_name: str = ""
    email: str = ""
    role_code: str = ""
    role_name: str = ""
    status: str = "ACTIVE"
