from dataclasses import dataclass

@dataclass
class Offer:
    offer_id: int | None = None
    offer_code: str = ""
    application_id: int = 0
    designation: str = ""
    offered_package_lpa: float = 0.0
    offer_status: str = "OFFERED"
