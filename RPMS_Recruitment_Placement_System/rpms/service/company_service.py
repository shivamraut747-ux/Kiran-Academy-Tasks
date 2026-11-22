
from rpms.exception.exceptions import CompanyNotFoundError, ValidationError
from rpms.util.validation import is_valid_email, is_valid_optional_mobile


class CompanyService:

    COMPANY_TYPES = ("MNC", "STARTUP", "MID_SIZE", "CONSULTANCY")
    STATUSES = ("ACTIVE", "INACTIVE")

    def __init__(self, company_dao):
        self.company_dao = company_dao

    def _validate(self, c):
        if not c.company_name or not c.company_name.strip():
            raise ValidationError("Please enter company name.")
        if not c.industry or not c.industry.strip():
            raise ValidationError("Please enter industry.")
        if not c.location or not c.location.strip():
            raise ValidationError("Please enter company location.")
        if not c.hr_name or not c.hr_name.strip():
            raise ValidationError("Please enter HR name.")
        if not is_valid_email(c.hr_email):
            raise ValidationError("Enter a valid HR email address.")
        if not is_valid_optional_mobile(c.hr_mobile):
            raise ValidationError("HR mobile number must contain 10 digits.")
        if c.company_type not in self.COMPANY_TYPES:
            raise ValidationError("Company type must be one of: " + ", ".join(self.COMPANY_TYPES))
        if c.status not in self.STATUSES:
            raise ValidationError("Status must be ACTIVE or INACTIVE.")

    def _next_code(self):
        """Creates codes like COM-009 (same format as the sample data)."""
        return f"COM-{self.company_dao.last_code_number('COM-') + 1:03d}"

    def add_company(self, company):
        self._validate(company)
        company.company_code = self._next_code()
        return self.company_dao.save(company)

    def update_company(self, company):
        self.get_company(company.company_id)                # must exist
        self._validate(company)
        self.company_dao.update(company)

    def get_company(self, company_id):
        company = self.company_dao.find_by_id(company_id)
        if not company:
            raise CompanyNotFoundError(f"Company ID {company_id} not found")
        return company

    def get_all_companies(self):
        return self.company_dao.find_all()

    def search_companies(self, filters):
        clean = {k: v for k, v in filters.items() if v not in (None, "")}
        return self.company_dao.search(clean)

    def set_status(self, company_id, status):
        """Activate / deactivate. Companies are never deleted (jobs may refer to them)."""
        if status not in self.STATUSES:
            raise ValidationError("Status must be ACTIVE or INACTIVE.")
        company = self.get_company(company_id)
        if company.status == status:
            raise ValidationError(f"Company is already {status}.")
        self.company_dao.update_status(company_id, status)
        return company
