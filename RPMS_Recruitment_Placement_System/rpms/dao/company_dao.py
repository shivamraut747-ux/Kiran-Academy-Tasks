from rpms.model.company import Company
from rpms.util.db_connection import fetch_all, fetch_one, execute

# open_jobs is counted with a sub-query so the list can show "4 Open Jobs"
BASE_SELECT = """
    SELECT c.*,
           (SELECT COUNT(*) FROM jobs j
             WHERE j.company_id = c.company_id AND j.status = 'OPEN') AS open_jobs
    FROM companies c
"""


class CompanyDAO:

    def last_code_number(self, prefix: str) -> int:
        row = fetch_one(
            "SELECT MAX(CAST(SUBSTRING_INDEX(company_code,'-',-1) AS UNSIGNED)) AS n "
            "FROM companies WHERE company_code LIKE %s",
            (prefix + "%",)
        )
        return int(row["n"] or 0)

    def save(self, c: Company) -> int:
        return execute(
            """INSERT INTO companies
               (company_code, company_name, industry, website, location, company_type,
                hr_name, hr_email, hr_mobile, status)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (c.company_code, c.company_name, c.industry, c.website or None, c.location,
             c.company_type, c.hr_name, c.hr_email, c.hr_mobile or None, c.status)
        )

    def update(self, c: Company):
        execute(
            """UPDATE companies SET company_name=%s, industry=%s, website=%s, location=%s,
                      company_type=%s, hr_name=%s, hr_email=%s, hr_mobile=%s, status=%s
               WHERE company_id=%s""",
            (c.company_name, c.industry, c.website or None, c.location, c.company_type,
             c.hr_name, c.hr_email, c.hr_mobile or None, c.status, c.company_id)
        )

    def update_status(self, company_id: int, status: str):
        execute("UPDATE companies SET status=%s WHERE company_id=%s", (status, company_id))

    def find_by_id(self, company_id: int):
        row = fetch_one(BASE_SELECT + " WHERE c.company_id=%s", (company_id,))
        return self._map(row) if row else None

    def find_all(self):
        return [self._map(r) for r in fetch_all(BASE_SELECT + " ORDER BY c.company_id")]

    def search(self, filters: dict):
        """filters keys (optional): name, location, status, company_type."""
        sql = BASE_SELECT + " WHERE 1=1"
        params = []
        if filters.get("name"):
            sql += " AND c.company_name LIKE %s"
            params.append(f"%{filters['name']}%")
        if filters.get("location"):
            sql += " AND c.location LIKE %s"
            params.append(f"%{filters['location']}%")
        if filters.get("status"):
            sql += " AND c.status=%s"
            params.append(filters["status"])
        if filters.get("company_type"):
            sql += " AND c.company_type=%s"
            params.append(filters["company_type"])
        sql += " ORDER BY c.company_id"
        return [self._map(r) for r in fetch_all(sql, tuple(params))]

    @staticmethod
    def _map(row):
        return Company(
            company_id=row["company_id"],
            company_code=row["company_code"],
            company_name=row["company_name"],
            industry=row["industry"] or "",
            location=row["location"] or "",
            hr_name=row["hr_name"] or "",
            hr_email=row["hr_email"] or "",
            status=row["status"],
            website=row["website"] or "",
            company_type=row["company_type"] or "",
            hr_mobile=row["hr_mobile"] or "",
            open_jobs=int(row.get("open_jobs") or 0)
        )
