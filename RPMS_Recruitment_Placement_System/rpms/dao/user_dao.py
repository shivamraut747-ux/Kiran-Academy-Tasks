from rpms.model.user import User
from rpms.util.db_connection import fetch_all, fetch_one, execute

BASE_SELECT = """
    SELECT u.user_id, u.username, u.full_name, u.email, u.status,
           r.role_code, r.role_name
    FROM users u JOIN roles r ON r.role_id = u.role_id
"""


class UserDAO:

    def find_by_username(self, username: str):
        row = fetch_one(BASE_SELECT + " WHERE u.username=%s", (username,))
        return self._map(row) if row else None

    def find_all_active(self):
        rows = fetch_all(BASE_SELECT + " WHERE u.status='ACTIVE' ORDER BY u.user_id")
        return [self._map(r) for r in rows]

    def update_last_login(self, user_id: int):
        execute("UPDATE users SET last_login_at=NOW() WHERE user_id=%s", (user_id,))

    @staticmethod
    def _map(row):
        return User(
            user_id=row["user_id"], username=row["username"], full_name=row["full_name"],
            email=row["email"] or "", role_code=row["role_code"],
            role_name=row["role_name"], status=row["status"]
        )
