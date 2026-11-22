from datetime import date

from rpms.exception.exceptions import (
    JobNotFoundError, CompanyNotFoundError, ValidationError
)
from rpms.util.db_connection import transaction
from rpms.util.validation import is_valid_percentage, is_valid_year


class JobService:

    EMPLOYMENT_TYPES = ("FULL_TIME", "INTERNSHIP", "CONTRACT")
    STATUSES = ("DRAFT", "OPEN", "CLOSED", "CANCELLED")

    def __init__(self, job_dao, company_dao, skill_dao):
        self.job_dao = job_dao
        self.company_dao = company_dao
        self.skill_dao = skill_dao

    # ---------- rules used by create and update ----------
    def _validate(self, j):
        if not j.job_title or not j.job_title.strip():
            raise ValidationError("Please enter job title.")
        if not j.location or not j.location.strip():
            raise ValidationError("Please enter job location.")
        if j.employment_type not in self.EMPLOYMENT_TYPES:
            raise ValidationError("Employment type must be one of: " + ", ".join(self.EMPLOYMENT_TYPES))
        if j.openings is None or j.openings <= 0:
            raise ValidationError("Number of openings must be greater than zero.")
        if j.min_package_lpa and j.max_package_lpa and j.min_package_lpa > j.max_package_lpa:
            raise ValidationError("Minimum package cannot exceed maximum package.")
        if j.min_package_lpa < 0 or j.max_package_lpa < 0:
            raise ValidationError("Package cannot be negative.")
        if not is_valid_percentage(j.min_percentage):
            raise ValidationError("Percentage must be between 0 and 100.")
        for year in (j.min_passing_year, j.max_passing_year):
            if year and not is_valid_year(year):
                raise ValidationError("Enter a valid passing year (for example 2025).")
        if j.min_passing_year and j.max_passing_year and j.min_passing_year > j.max_passing_year:
            raise ValidationError("Minimum passing year cannot be greater than maximum passing year.")
        if j.max_backlogs is None or j.max_backlogs < 0:
            raise ValidationError("Maximum backlogs cannot be negative.")
        if not j.posted_date:
            raise ValidationError("Please enter posted date.")
        if not j.application_deadline:
            raise ValidationError("Please enter application deadline.")
        if j.application_deadline < j.posted_date:
            raise ValidationError("Application deadline cannot be before posted date.")
        if j.status not in self.STATUSES:
            raise ValidationError("Status must be one of: " + ", ".join(self.STATUSES))

    def _skill_ids(self, skill_names):
        """Turns ['Java','SQL'] into [1,3]. Unknown names are rejected."""
        ids = []
        for name in skill_names:
            skill_id = self.skill_dao.find_id_by_name(name.strip())
            if skill_id is None:
                raise ValidationError(f"Unknown skill: {name.strip()}")
            if skill_id not in ids:
                ids.append(skill_id)
        return ids

    def _next_code(self):
        """Creates codes like JOB-2026-013."""
        prefix = f"JOB-{date.today().year}-"
        return f"{prefix}{self.job_dao.last_code_number(prefix) + 1:03d}"

    # ---------- operations ----------
    def create_job(self, job, skill_names, created_by):
        company = self.company_dao.find_by_id(job.company_id)
        if not company:
            raise CompanyNotFoundError(f"Company ID {job.company_id} not found")
        if company.status != "ACTIVE":
            raise ValidationError("Jobs can only be created for ACTIVE companies.")
        self._validate(job)
        skill_ids = self._skill_ids(skill_names)       # check before saving anything

        job.job_code = self._next_code()
        job.created_by = created_by

        # Two tables change (jobs + job_skills) -> one transaction.
        with transaction() as con:
            job_id = self.job_dao.save(job, con)
            self.job_dao.replace_skills(job_id, skill_ids, con)
        return job_id, job.job_code

    def update_job(self, job, skill_names=None):
        """skill_names=None means 'leave skills as they are'."""
        self.get_job(job.job_id)                         # must exist
        self._validate(job)
        skill_ids = self._skill_ids(skill_names) if skill_names is not None else None
        with transaction() as con:
            self.job_dao.update(job, con)
            if skill_ids is not None:
                self.job_dao.replace_skills(job.job_id, skill_ids, con)

    def close_job(self, job_id):
        job = self.get_job(job_id)
        if job.status in ("CLOSED", "CANCELLED"):
            raise ValidationError(f"Job is already {job.status}.")
        self.job_dao.update_status(job_id, "CLOSED")
        return job

    def get_job(self, job_id):
        job = self.job_dao.find_by_id(job_id)
        if not job:
            raise JobNotFoundError(f"Job ID {job_id} not found")
        return job

    def get_job_details(self, job_id):
        job = self.job_dao.find_details(job_id)
        if not job:
            raise JobNotFoundError(f"Job ID {job_id} not found")
        return job

    def get_open_jobs(self):
        return self.job_dao.search({"status": "OPEN"})

    def search_jobs(self, filters):
        clean = {k: v for k, v in filters.items() if v not in (None, "")}
        return self.job_dao.search(clean)
