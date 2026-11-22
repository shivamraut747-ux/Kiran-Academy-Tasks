from rpms.util.console_input import ask_int, ask_text, ask_date, ask_choice, ask_float, ask_time
from rpms.util.display import print_table
from rpms.service.interview_service import InterviewService


def _show(rows):
    print_table(["ID", "Application", "Candidate", "Company", "Round", "Type", "Date",
                 "Time", "Mode", "Interviewer", "Status"], [list(r.values()) for r in rows])


def interview_menu(service, log_service):
    while True:
        print("\n------ INTERVIEWS ------")
        print("1. Schedule Interview")
        print("2. Reschedule Interview")
        print("3. Add Feedback / Complete Interview")
        print("4. Mark No Show")
        print("5. Pending Interviews")
        print("6. Search Interviews")
        print("0. Back")
        choice = input("Enter Choice: ").strip()
        try:
            if choice == "1":
                app_id = ask_int("Application ID", required=True)
                iid = service.schedule(
                    app_id, ask_choice("Round", InterviewService.ROUND_TYPES),
                    ask_date("Interview date", required=True), ask_time("Interview time"),
                    ask_choice("Mode", InterviewService.MODES),
                    ask_text("Interviewer name") or None, ask_text("Meeting link / venue") or None)
                print(f"Interview scheduled. ID = {iid}")
                log_service.log(f"Interview Scheduled: id {iid}, application {app_id}")
            elif choice == "2":
                iid = ask_int("Interview ID", required=True)
                service.reschedule(iid, ask_date("New date", required=True), ask_time("New time"))
                print("Interview rescheduled.")
                log_service.log(f"Interview Rescheduled: id {iid}")
            elif choice == "3":
                iid = ask_int("Interview ID", required=True)
                print("Ratings 0-5 (Enter to skip)")
                service.add_feedback(
                    iid, ask_float("Technical rating"), ask_float("Communication rating"),
                    ask_float("Problem solving rating"), ask_float("Overall rating"),
                    ask_choice("Result", InterviewService.RECOMMENDATIONS),
                    ask_text("Remarks") or None)
                print("Feedback saved. Interview completed.")
                log_service.log(f"Interview Feedback: id {iid}")
            elif choice == "4":
                iid = ask_int("Interview ID", required=True)
                service.mark_no_show(iid)
                print("Interview marked NO_SHOW.")
                log_service.log(f"Interview No Show: id {iid}")
            elif choice == "5":
                _show(service.search(pending_only=True))
            elif choice == "6":
                _show(service.search(
                    status=ask_choice("Status", ["SCHEDULED", "COMPLETED", "RESCHEDULED", "CANCELLED", "NO_SHOW"], required=False) or None,
                    candidate_name=ask_text("Candidate name") or None,
                    date_from=ask_date("Date from"), date_to=ask_date("Date to")))
            elif choice == "0":
                return
            else:
                print("Invalid choice.")
        except Exception as exc:
            print("ERROR:", exc)
