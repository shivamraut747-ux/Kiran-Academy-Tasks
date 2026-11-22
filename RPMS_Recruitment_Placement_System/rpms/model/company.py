from dataclasses import dataclass

@dataclass
class Company:
    company_id: int | None = None
    company_code: str = ""
    company_name: str = ""
    industry: str = ""
    location: str = ""
    hr_name: str = ""
    hr_email: str = ""
    status: str = "ACTIVE"
    # added in Phase 2
    website: str = ""
    company_type: str = ""
    hr_mobile: str = ""
    open_jobs: int = 0          # only filled by list/search (not saved)
