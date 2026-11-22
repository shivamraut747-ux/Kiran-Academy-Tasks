from rpms.util.console_input import ask_int, ask_text, ask_date, ask_choice, ask_float
from rpms.util.display import print_table
from rpms.service.placement_service import JOINING_STATUSES
from rpms.service.transaction_demo import rollback_demo


def offer_menu(service, log_service):
    while True:
        print("\n------ OFFERS ------")
        print("1. Create Offer (for SELECTED application)")
        print("2. Update Offer Status")
        print("3. View Offers")
        print("0. Back")
        choice = input("Enter Choice: ").strip()
        try:
            if choice == "1":
                app_id = ask_int("Application ID", required=True)
                oid = service.create_offer(
                    app_id, ask_text("Designation", required=True),
                    ask_float("Package (LPA)", required=True),
                    ask_date("Offer date (Enter = today)"), ask_date("Expected joining date"))
                print(f"Offer created. ID = {oid}")
                log_service.log(f"Offer Created: id {oid}, application {app_id}")
            elif choice == "2":
                oid = ask_int("Offer ID", required=True)
                new = ask_choice("New status", ["ACCEPTED", "REJECTED", "EXPIRED", "WITHDRAWN"])
                service.update_status(oid, new, ask_text("Remarks (optional)") or None)
                print("Offer status updated.")
                log_service.log(f"Offer {new}: id {oid}")
            elif choice == "3":
                rows = service.search(ask_choice("Status filter", ["OFFERED", "ACCEPTED", "REJECTED", "EXPIRED", "WITHDRAWN"], required=False) or None)
                print_table(["ID", "Code", "Application", "Candidate", "Company", "Designation",
                             "LPA", "Offer date", "Joining", "Status"], [list(r.values()) for r in rows])
            elif choice == "0":
                return
            else:
                print("Invalid choice.")
        except Exception as exc:
            print("ERROR:", exc)


def placement_menu(service, log_service):
    while True:
        print("\n------ PLACEMENTS ------")
        print("1. Confirm Joining (from ACCEPTED offer)")
        print("2. Update Joining Status (PENDING / DEFERRED placement)")
        print("3. View Placements")
        print("4. Demo: Transaction Rollback")
        print("0. Back")
        choice = input("Enter Choice: ").strip()
        try:
            if choice == "1":
                oid = ask_int("Offer ID", required=True)
                status = ask_choice("Joining status", JOINING_STATUSES)
                date_ = ask_date("Actual joining date", required=(status == "JOINED"))
                pid = service.confirm_joining(oid, status, date_)
                print(f"Placement saved. ID = {pid}")
                log_service.log(f"Placement {status}: id {pid}, offer {oid}")
            elif choice == "2":
                pid = ask_int("Placement ID", required=True)
                status = ask_choice("New joining status", JOINING_STATUSES)
                service.update_joining(pid, status, ask_date("Actual joining date", required=(status == "JOINED")))
                print("Placement updated.")
                log_service.log(f"Placement updated: id {pid} -> {status}")
            elif choice == "3":
                rows = service.search(ask_choice("Joining status filter", JOINING_STATUSES, required=False) or None)
                print_table(["ID", "Candidate", "Name", "Company", "Designation", "LPA",
                             "Expected", "Actual", "Joining", "Status"], [list(r.values()) for r in rows])
            elif choice == "4":
                for line in rollback_demo():
                    print(line)
            elif choice == "0":
                return
            else:
                print("Invalid choice.")
        except Exception as exc:
            print("ERROR:", exc)
