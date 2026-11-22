from rpms.util.console_input import ask_int, ask_text, ask_date, ask_choice
from rpms.util.display import print_table
from rpms.util.workflow import ALL_STATUSES


def _show(rows):
    headers = ["ID", "Code", "Candidate", "Name", "Company", "Job", "Title",
               "Eligibility", "Status", "Applied"]
    print_table(headers, [list(r.values()) for r in rows])


def applications_menu(application_service, log_service):
    while True:
        print("\n------ APPLICATIONS ------")
        print("1. Apply for Job")
        print("2. View / Search Applications")
        print("3. Check Eligibility (existing application)")
        print("4. Shortlist")
        print("5. Reject")
        print("6. Withdraw")
        print("7. View Application History")
        print("8. Pipeline Summary")
        print("0. Back")
        choice = input("Enter Choice: ").strip()
        try:
            if choice == "1":
                cid = ask_int("Candidate ID", required=True)
                jid = ask_int("Job ID", required=True)
                app_id = application_service.apply_for_job(cid, jid)
                print(f"Application created. ID = {app_id}")
                log_service.log(f"Application created: candidate={cid}, job={jid}")
            elif choice == "2":
                print("Leave a filter empty to skip it.")
                rows = application_service.search(
                    application_code=ask_text("Application code") or None,
                    candidate_name=ask_text("Candidate name") or None,
                    company=ask_text("Company") or None,
                    job_code=ask_text("Job code") or None,
                    status=ask_choice("Status", ALL_STATUSES, required=False) or None,
                    date_from=ask_date("Applied from"), date_to=ask_date("Applied to"))
                _show(rows)
            elif choice == "3":
                app_id = ask_int("Application ID", required=True)
                ok, reasons = application_service.verify_eligibility(app_id)
                print("ELIGIBLE" if ok else "NOT ELIGIBLE: " + "; ".join(reasons))
                log_service.log(f"Eligibility checked: APP id {app_id}")
            elif choice == "4":
                app_id = ask_int("Application ID", required=True)
                application_service.shortlist(app_id, ask_text("Remarks (optional)") or None)
                print("Application shortlisted.")
                log_service.log(f"Candidate Shortlisted: APP id {app_id}")
            elif choice == "5":
                app_id = ask_int("Application ID", required=True)
                application_service.reject(app_id, ask_text("Reason", required=True))
                print("Application rejected.")
                log_service.log(f"Application Rejected: APP id {app_id}")
            elif choice == "6":
                app_id = ask_int("Application ID", required=True)
                application_service.withdraw(app_id, ask_text("Remarks (optional)") or None)
                print("Application withdrawn.")
                log_service.log(f"Application Withdrawn: APP id {app_id}")
            elif choice == "7":
                app_id = ask_int("Application ID", required=True)
                rows = application_service.get_history(app_id)
                print_table(["ID", "From", "To", "Remarks", "Changed by", "When"],
                            [list(r.values()) for r in rows])
            elif choice == "8":
                summary = application_service.status_summary()
                print_table(["Status", "Count"], [[k, v] for k, v in summary.items()])
            elif choice == "0":
                return
            else:
                print("Invalid choice.")
        except Exception as exc:
            print("ERROR:", exc)
