from dataclasses import dataclass

@dataclass
class Placement:
    placement_id: int | None = None
    candidate_id: int = 0
    company_id: int = 0
    job_id: int = 0
    final_package_lpa: float = 0.0
    joining_status: str = "PENDING"
