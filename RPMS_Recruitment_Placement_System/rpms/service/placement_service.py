from datetime import date

from rpms.exception.exceptions import (
    OfferNotFoundError, PlacementNotFoundError, DuplicatePlacementError, ValidationError
)
from rpms.util.db_connection import transaction
from rpms.util.session import get_current_user_id

JOINING_STATUSES = ("PENDING", "JOINED", "NOT_JOINED", "DEFERRED", "NO_SHOW")


class PlacementService:

    def __init__(self, placement_dao, offer_dao, application_service):
        self.placement_dao = placement_dao
        self.offer_dao = offer_dao
        self.application_service = application_service

    @staticmethod
    def _check(joining_status, actual_date):
        if joining_status not in JOINING_STATUSES:
            raise ValidationError("Joining status must be one of: " + ", ".join(JOINING_STATUSES))
        if joining_status == "JOINED":
            if actual_date is None:
                raise ValidationError("Actual joining date is required when status is JOINED.")
            if actual_date > date.today():
                raise ValidationError("Actual joining date cannot be in the future.")

    def _mark_joined(self, candidate_id, application_id, con):
        """update candidate placement status -> update application -> insert history"""
        self.placement_dao.mark_candidate_placed(candidate_id, con)
        self.application_service.change_status(application_id, "JOINED", "Candidate joined company", con)

    def confirm_joining(self, offer_id, joining_status="JOINED", actual_date=None):
        """Joining confirmation -> create placement -> (if JOINED) candidate PLACED + application JOINED + history."""
        if get_current_user_id() is None:
            raise ValidationError("Please log in first.")
        self._check(joining_status, actual_date)
        with transaction() as con:
            offer = self.offer_dao.find_by_id(offer_id, con, lock=True)
            if not offer:
                raise OfferNotFoundError("Offer not found")
            if offer["offer_status"] != "ACCEPTED":
                raise ValidationError(
                    f"Joining can be confirmed only for an ACCEPTED offer (status is {offer['offer_status']}).")
            if self.placement_dao.find_by_offer(offer_id, con):
                raise DuplicatePlacementError("A placement already exists for this offer.")
            ctx = self.offer_dao.context(offer_id, con)
            placement_id = self.placement_dao.insert(ctx, joining_status, actual_date, con)
            if joining_status == "JOINED":
                self._mark_joined(ctx["candidate_id"], ctx["application_id"], con)
        return placement_id

    def update_joining(self, placement_id, new_status, actual_date=None):
        """Change a PENDING / DEFERRED placement (for example to JOINED)."""
        if get_current_user_id() is None:
            raise ValidationError("Please log in first.")
        self._check(new_status, actual_date)
        with transaction() as con:
            p = self.placement_dao.find_by_id(placement_id, con, lock=True)
            if not p:
                raise PlacementNotFoundError("Placement not found")
            if p["joining_status"] not in ("PENDING", "DEFERRED"):
                raise ValidationError(f"Placement is already {p['joining_status']} and cannot change.")
            if new_status == p["joining_status"]:
                raise ValidationError("Joining status is already " + new_status + ".")
            self.placement_dao.update_joining(placement_id, new_status, actual_date, con)
            if new_status == "JOINED":
                self._mark_joined(p["candidate_id"], p["application_id"], con)

    def search(self, joining_status=None):
        return self.placement_dao.search(joining_status)
