from rpms.model.application import Application
from rpms.util.db_connection import (
    get_connection, fetch_all as _fetch_all, fetch_one as _fetch_one, execute as _execute
)

class ApplicationDAO:

    def save(self, app: Application) -> int:
        sql = '''
            INSERT INTO applications
            (application_code,candidate_id,job_id,eligibility_status,
             eligibility_reason,application_status)
            VALUES (%s,%s,%s,%s,%s,%s)
        '''
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute(sql, (
                app.application_code,
                app.candidate_id,
                app.job_id,
                app.eligibility_status,
                app.eligibility_reason,
                app.application_status
            ))
            con.commit()
            return cur.lastrowid
        finally:
            con.close()

    def exists(self, candidate_id: int, job_id: int) -> bool:
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT 1 FROM applications WHERE candidate_id=%s AND job_id=%s",
                (candidate_id, job_id)
            )
            return cur.fetchone() is not None
        finally:
            con.close()

    def find_by_candidate(self, candidate_id: int):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute(
                "SELECT * FROM applications WHERE candidate_id=%s ORDER BY application_id DESC",
                (candidate_id,)
            )
            return cur.fetchall()
        finally:
            con.close()

    # ----- Added in Phase 3: methods that can join a transaction (con) -----

    def next_code(self, year: int, con=None) -> str:
        """Next business code like APP-2026-0041."""
        row = _fetch_one(
            """SELECT COALESCE(MAX(CAST(SUBSTRING_INDEX(application_code,'-',-1) AS UNSIGNED)),0) AS n
               FROM applications WHERE application_code LIKE %s""",
            (f"APP-{year}-%",), con)
        return f"APP-{year}-{int(row['n']) + 1:04d}"

    def save_tx(self, app, recruiter_id, source, con=None) -> int:
        sql = """INSERT INTO applications
                 (application_code,candidate_id,job_id,eligibility_status,
                  eligibility_reason,application_status,source,assigned_recruiter_id)
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
        return _execute(sql, (app.application_code, app.candidate_id, app.job_id,
                              app.eligibility_status, app.eligibility_reason,
                              app.application_status, source, recruiter_id), con)

    def find_by_id(self, application_id, con=None, lock=False):
        """Return one application row (dict) or None. lock=True adds FOR UPDATE."""
        sql = "SELECT * FROM applications WHERE application_id=%s"
        if lock:
            sql += " FOR UPDATE"      # blocks other users from changing it at the same time
        return _fetch_one(sql, (application_id,), con)

    def update_status(self, application_id, new_status, con=None):
        _execute("UPDATE applications SET application_status=%s, updated_at=NOW() "
                 "WHERE application_id=%s", (new_status, application_id), con)

    def update_eligibility(self, application_id, status, reason, con=None):
        _execute("UPDATE applications SET eligibility_status=%s, eligibility_reason=%s, "
                 "updated_at=NOW() WHERE application_id=%s",
                 (status, reason[:500], application_id), con)

    def search(self, application_code=None, candidate_name=None, company=None,
               job_code=None, status=None, date_from=None, date_to=None):
        """Search with optional filters. Only fixed SQL text is joined; values are parameters."""
        sql = """SELECT a.application_id, a.application_code, c.candidate_code, c.full_name,
                        co.company_name, j.job_code, j.job_title, a.eligibility_status,
                        a.application_status, DATE(a.applied_at) AS applied_on
                 FROM applications a
                 JOIN candidates c ON c.candidate_id = a.candidate_id
                 JOIN jobs j ON j.job_id = a.job_id
                 JOIN companies co ON co.company_id = j.company_id
                 WHERE 1=1"""
        params = []
        if application_code:
            sql += " AND a.application_code LIKE %s"; params.append(f"%{application_code}%")
        if candidate_name:
            sql += " AND c.full_name LIKE %s"; params.append(f"%{candidate_name}%")
        if company:
            sql += " AND co.company_name LIKE %s"; params.append(f"%{company}%")
        if job_code:
            sql += " AND j.job_code LIKE %s"; params.append(f"%{job_code}%")
        if status:
            sql += " AND a.application_status=%s"; params.append(status)
        if date_from:
            sql += " AND DATE(a.applied_at) >= %s"; params.append(date_from)
        if date_to:
            sql += " AND DATE(a.applied_at) <= %s"; params.append(date_to)
        sql += " ORDER BY a.application_id DESC"
        return _fetch_all(sql, tuple(params))

    def count_by_status(self):
        return _fetch_all("SELECT application_status, COUNT(*) AS total FROM applications "
                          "GROUP BY application_status ORDER BY total DESC")
