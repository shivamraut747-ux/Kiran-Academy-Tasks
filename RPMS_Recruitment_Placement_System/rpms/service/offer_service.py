from datetime import date

from rpms.exception.exceptions import (
    ApplicationNotFoundError, OfferNotFoundError, DuplicateOfferError,
    InvalidStatusTransitionError, ValidationError
)
from rpms.util.db_connection import transaction
from rpms.util.session import get_current_user_id

OFFER_TRANSITIONS = {
    "OFFERED":   ["ACCEPTED", "REJECTED", "EXPIRED", "WITHDRAWN"],
    "ACCEPTED":  ["WITHDRAWN"],
    "REJECTED":  [], "EXPIRED": [], "WITHDRAWN": [],
}


class OfferService:

    def __init__(self, offer_dao, application_dao, placement_dao, application_service):
        self.offer_dao = offer_dao
        self.application_dao = application_dao
        self.placement_dao = placement_dao
        self.application_service = application_service

    def create_offer(self, application_id, designation, package_lpa, offer_date, joining_date=None):
        """Selection -> create offer -> application SELECTED->OFFERED -> history (one transaction)."""
        if get_current_user_id() is None:
            raise ValidationError("Please log in first.")
        if not designation or not designation.strip():
            raise ValidationError("Please enter designation.")
        if package_lpa is None or package_lpa <= 0:
            raise ValidationError("Package must be greater than zero.")
        if offer_date is None:
            offer_date = date.today()
        if joining_date and joining_date < offer_date:
            raise ValidationError("Joining date cannot be before offer date.")
        with transaction() as con:
            app = self.application_dao.find_by_id(application_id, con, lock=True)
            if not app:
                raise ApplicationNotFoundError("Application not found")
            if app["application_status"] != "SELECTED":
                raise ValidationError(
                    f"Offer can be created only for a SELECTED application (status is {app['application_status']}).")
            if self.offer_dao.find_by_application(application_id, con):
                raise DuplicateOfferError("An offer already exists for this application.")
            code = self.offer_dao.next_code(offer_date.year, con)
            offer_id = self.offer_dao.insert(code, application_id, designation.strip(),
                                             package_lpa, offer_date, joining_date, None, con)
            self.application_service.change_status(application_id, "OFFERED", f"Offer {code} created", con)
        return offer_id

    def update_status(self, offer_id, new_status, remarks=None):
        with transaction() as con:
            offer = self.offer_dao.find_by_id(offer_id, con, lock=True)
            if not offer:
                raise OfferNotFoundError("Offer not found")
            old = offer["offer_status"]
            if new_status not in OFFER_TRANSITIONS.get(old, []) :
                allowed = ", ".join(OFFER_TRANSITIONS.get(old, [])) or "none (final status)"
                raise InvalidStatusTransitionError(
                    f"Invalid offer status change {old} -> {new_status}. Allowed: {allowed}")
            if old == "ACCEPTED" and self.placement_dao.find_by_offer(offer_id, con):
                raise ValidationError("A placement already exists for this offer; it cannot be withdrawn.")
            self.offer_dao.set_status(offer_id, new_status, con)
            if new_status != "ACCEPTED":      # offer did not work out -> application is closed
                self.application_service.change_status(
                    offer["application_id"], "REJECTED",
                    f"Offer {new_status}" + (f": {remarks}" if remarks else ""), con)

    def search(self, status=None):
        return self.offer_dao.search(status)
