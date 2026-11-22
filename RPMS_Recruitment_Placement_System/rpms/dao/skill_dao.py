from rpms.util.db_connection import fetch_all, fetch_one


class SkillDAO:

    def find_all_active(self):
        return fetch_all("SELECT skill_id, skill_name, category FROM skills "
                         "WHERE is_active=1 ORDER BY skill_name")

    def find_id_by_name(self, name: str):
        row = fetch_one("SELECT skill_id FROM skills WHERE skill_name=%s AND is_active=1",
                        (name,))
        return row["skill_id"] if row else None
