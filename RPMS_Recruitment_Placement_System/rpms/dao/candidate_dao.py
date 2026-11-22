from rpms.model.candidate import Candidate
from rpms.util.db_connection import get_connection, fetch_all, fetch_one, execute

class CandidateDAO:

    def save(self, candidate: Candidate) -> int:
        sql = '''
            INSERT INTO candidates
            (candidate_code, full_name, email, mobile, qualification, passing_year,
             percentage, backlog_count, primary_technology, profile_status, placement_status,
             college, university, current_location, preferred_location)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,'ACTIVE','NOT_PLACED',%s,%s,%s,%s)
        '''
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute(sql, (
                candidate.candidate_code,
                candidate.full_name,
                candidate.email,
                candidate.mobile,
                candidate.qualification,
                candidate.passing_year,
                candidate.percentage,
                candidate.backlog_count,
                candidate.primary_technology,
                candidate.college or None,
                candidate.university or None,
                candidate.current_location or None,
                candidate.preferred_location or None
            ))
            con.commit()
            return cur.lastrowid
        finally:
            con.close()

    def find_by_id(self, candidate_id: int):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute("SELECT * FROM candidates WHERE candidate_id=%s", (candidate_id,))
            row = cur.fetchone()
            return self._map(row) if row else None
        finally:
            con.close()

    def find_by_email(self, email: str):
        return self._find_one("SELECT * FROM candidates WHERE email=%s", email)

    def find_by_mobile(self, mobile: str):
        return self._find_one("SELECT * FROM candidates WHERE mobile=%s", mobile)

    def _find_one(self, sql: str, value: str):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute(sql, (value,))
            row = cur.fetchone()
            return self._map(row) if row else None
        finally:
            con.close()

    def find_all(self):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute("SELECT * FROM candidates ORDER BY candidate_id")
            return [self._map(row) for row in cur.fetchall()]
        finally:
            con.close()

    def find_by_technology(self, technology: str):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute(
                "SELECT * FROM candidates WHERE primary_technology=%s ORDER BY full_name",
                (technology,)
            )
            return [self._map(row) for row in cur.fetchall()]
        finally:
            con.close()

    # ---------------- added in Phase 2 ----------------
    def last_code_number(self, prefix: str) -> int:
        """Highest number used so far for codes like CAN-2026-0007 (0 if none)."""
        row = fetch_one(
            "SELECT MAX(CAST(SUBSTRING_INDEX(candidate_code,'-',-1) AS UNSIGNED)) AS n "
            "FROM candidates WHERE candidate_code LIKE %s",
            (prefix + "%",)
        )
        return int(row["n"] or 0)

    def update(self, c: Candidate):
        execute(
            """UPDATE candidates SET full_name=%s, email=%s, mobile=%s, qualification=%s,
                      college=%s, university=%s, passing_year=%s, percentage=%s,
                      backlog_count=%s, primary_technology=%s, current_location=%s,
                      preferred_location=%s, profile_status=%s
               WHERE candidate_id=%s""",
            (c.full_name, c.email, c.mobile, c.qualification,
             c.college or None, c.university or None, c.passing_year, c.percentage,
             c.backlog_count, c.primary_technology or None, c.current_location or None,
             c.preferred_location or None, c.profile_status, c.candidate_id)
        )

    def update_profile_status(self, candidate_id: int, status: str):
        execute("UPDATE candidates SET profile_status=%s WHERE candidate_id=%s",
                (status, candidate_id))

    def search(self, filters: dict):
        """
        filters keys (all optional): candidate_code, full_name, mobile, email,
        technology, passing_year, qualification, status.
        Column names are written by us; user values always go in as %s parameters,
        so this is safe from SQL injection.
        """
        sql = "SELECT * FROM candidates WHERE 1=1"
        params = []
        for key, column in (("candidate_code", "candidate_code"), ("full_name", "full_name"),
                            ("mobile", "mobile"), ("email", "email")):
            if filters.get(key):
                sql += f" AND {column} LIKE %s"
                params.append(f"%{filters[key]}%")
        if filters.get("technology"):
            sql += " AND primary_technology=%s"
            params.append(filters["technology"])
        if filters.get("passing_year"):
            sql += " AND passing_year=%s"
            params.append(filters["passing_year"])
        if filters.get("qualification"):
            sql += " AND qualification=%s"
            params.append(filters["qualification"])
        if filters.get("status"):
            # UI dropdown mixes both kinds of status: PLACED is a placement status
            if filters["status"] == "PLACED":
                sql += " AND placement_status='PLACED'"
            else:
                sql += " AND profile_status=%s"
                params.append(filters["status"])
        sql += " ORDER BY candidate_id"
        return [self._map(row) for row in fetch_all(sql, tuple(params))]

    @staticmethod
    def _map(row):
        return Candidate(
            candidate_id=row["candidate_id"],
            candidate_code=row["candidate_code"],
            full_name=row["full_name"],
            email=row["email"],
            mobile=row["mobile"],
            qualification=row["qualification"],
            passing_year=row["passing_year"],
            percentage=float(row["percentage"] or 0),
            backlog_count=row["backlog_count"],
            primary_technology=row["primary_technology"] or "",
            profile_status=row["profile_status"],
            placement_status=row["placement_status"],
            college=row.get("college") or "",
            university=row.get("university") or "",
            current_location=row.get("current_location") or "",
            preferred_location=row.get("preferred_location") or ""
        )
