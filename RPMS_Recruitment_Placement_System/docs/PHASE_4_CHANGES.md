# Phase 4 - Interviews, Offers, Placements

New: dao/interview_dao.py, offer_dao.py, placement_dao.py; service/interview_service.py, offer_service.py,
placement_service.py, transaction_demo.py; app/interview_menu.py, offer_placement_menu.py; tests/test_phase4.py.
Changed: exceptions.py (7 new errors), console_input.py (ask_time), main.py (menus 5, 6, 7 wired).
Sample data (sql/rpms_sample_data.sql + rpms_full_setup.sql): now 8 offers, 5 placements. Application statuses
of offered/joined sample applications were made consistent (OFFERED / JOINED) and history rows added.
Models (interview/offer/placement) are not used yet: rows are plain dicts, like Phase 3.

## Transactions (Database PDF section 28)
- Schedule: insert round + SHORTLISTED/INTERVIEWED -> INTERVIEW_SCHEDULED + history
- Feedback: insert feedback + interview COMPLETED + application INTERVIEWED (+ SELECTED/REJECTED) + history
- Offer: insert offer + SELECTED -> OFFERED + history
- Joining: insert placement + candidate PLACED + OFFERED -> JOINED + history
- Offer rejected/expired/withdrawn: offer status + application REJECTED + history
Rollback demo: Placements menu option 4, and tests.test_phase4.test_rollback_on_joining_failure.

## Test
python -m unittest tests.test_phase4 -v      (needs MySQL; reload sql/rpms_full_setup.sql first)
