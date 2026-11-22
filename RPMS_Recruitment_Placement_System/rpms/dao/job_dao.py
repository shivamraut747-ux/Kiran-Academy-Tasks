from rpms.model.job import Job
from rpms.util.db_connection import get_connection, fetch_all, fetch_one, execute

# company name + comma-separated skills are added for list screens
LIST_SELECT = """
    SELECT j.*, c.company_name,
           (SELECT GROUP_CONCAT(s.skill_name ORDER BY s.skill_name SEPARATOR ', ')
              FROM job_skills js JOIN skills s ON s.skill_id = js.skill_id
             WHERE js.job_id = j.job_id) AS skills
    FROM jobs j JOIN companies c ON c.company_id = j.company_id
"""


class JobDAO:

    def find_by_id(self, job_id: int):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute("SELECT * FROM jobs WHERE job_id=%s", (job_id,))
            row = cur.fetchone()
            return self._map(row) if row else None
        finally:
            con.close()

    def find_open_jobs(self):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute("SELECT * FROM jobs WHERE status='OPEN' ORDER BY job_id")
            return [self._map(row) for row in cur.fetchall()]
        finally:
            con.close()

    # ---------------- added in Phase 2 ----------------
    def last_code_number(self, prefix: str) -> int:
        row = fetch_one(
            "SELECT MAX(CAST(SUBSTRING_INDEX(job_code,'-',-1) AS UNSIGNED)) AS n "
            "FROM jobs WHERE job_code LIKE %s",
            (prefix + "%",)
        )
        return int(row["n"] or 0)

    def find_details(self, job_id: int):
        """Same as find_by_id but also fills company_name and skills."""
        row = fetch_one(LIST_SELECT + " WHERE j.job_id=%s", (job_id,))
        return self._map(row) if row else None

    def save(self, j: Job, con=None) -> int:
        return execute(
            """INSERT INTO jobs
               (job_code, company_id, job_title, employment_type, location, openings,
                min_package_lpa, max_package_lpa, min_percentage, min_passing_year,
                max_passing_year, max_backlogs, qualification_rule, posted_date,
                application_deadline, status, created_by)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (j.job_code, j.company_id, j.job_title, j.employment_type, j.location,
             j.openings, j.min_package_lpa or None, j.max_package_lpa or None,
             j.min_percentage or None, j.min_passing_year or None,
             j.max_passing_year or None, j.max_backlogs, j.qualification_rule or None,
             j.posted_date, j.application_deadline, j.status, j.created_by),
            con
        )

    def update(self, j: Job, con=None):
        execute(
            """UPDATE jobs SET job_title=%s, employment_type=%s, location=%s, openings=%s,
                      min_package_lpa=%s, max_package_lpa=%s, min_percentage=%s,
                      min_passing_year=%s, max_passing_year=%s, max_backlogs=%s,
                      qualification_rule=%s, posted_date=%s, application_deadline=%s,
                      status=%s
               WHERE job_id=%s""",
            (j.job_title, j.employment_type, j.location, j.openings,
             j.min_package_lpa or None, j.max_package_lpa or None,
             j.min_percentage or None, j.min_passing_year or None,
             j.max_passing_year or None, j.max_backlogs, j.qualification_rule or None,
             j.posted_date, j.application_deadline, j.status, j.job_id),
            con
        )

    def update_status(self, job_id: int, status: str, con=None):
        execute("UPDATE jobs SET status=%s WHERE job_id=%s", (status, job_id), con)

    def replace_skills(self, job_id: int, skill_ids: list, con=None):
        """Remove the old skill list of a job and save the new one."""
        execute("DELETE FROM job_skills WHERE job_id=%s", (job_id,), con)
        for skill_id in skill_ids:
            execute("INSERT INTO job_skills (job_id, skill_id) VALUES (%s,%s)",
                    (job_id, skill_id), con)

    def search(self, filters: dict):
        """filters keys (optional): job_code, company_id, technology, location,
        status, employment_type."""
        sql = LIST_SELECT + " WHERE 1=1"
        params = []
        if filters.get("job_code"):
            sql += " AND j.job_code LIKE %s"
            params.append(f"%{filters['job_code']}%")
        if filters.get("company_id"):
            sql += " AND j.company_id=%s"
            params.append(filters["company_id"])
        if filters.get("technology"):
            sql += (" AND EXISTS (SELECT 1 FROM job_skills js2 "
                    "JOIN skills s2 ON s2.skill_id = js2.skill_id "
                    "WHERE js2.job_id = j.job_id AND s2.skill_name LIKE %s)")
            params.append(f"%{filters['technology']}%")
        if filters.get("location"):
            sql += " AND j.location LIKE %s"
            params.append(f"%{filters['location']}%")
        if filters.get("status"):
            sql += " AND j.status=%s"
            params.append(filters["status"])
        if filters.get("employment_type"):
            sql += " AND j.employment_type=%s"
            params.append(filters["employment_type"])
        sql += " ORDER BY j.job_id"
        return [self._map(r) for r in fetch_all(sql, tuple(params))]

    @staticmethod
    def _map(row):
        return Job(
            job_id=row["job_id"],
            job_code=row["job_code"],
            company_id=row["company_id"],
            job_title=row["job_title"],
            location=row["location"],
            openings=row["openings"],
            min_package_lpa=float(row["min_package_lpa"] or 0),
            max_package_lpa=float(row["max_package_lpa"] or 0),
            min_percentage=float(row["min_percentage"] or 0),
            min_passing_year=row["min_passing_year"] or 0,
            max_passing_year=row["max_passing_year"] or 0,
            max_backlogs=row["max_backlogs"],
            application_deadline=row["application_deadline"],
            status=row["status"],
            employment_type=row.get("employment_type") or "FULL_TIME",
            posted_date=row.get("posted_date"),
            qualification_rule=row.get("qualification_rule") or "",
            created_by=row.get("created_by"),
            company_name=row.get("company_name") or "",
            skills=row.get("skills") or ""
        )
