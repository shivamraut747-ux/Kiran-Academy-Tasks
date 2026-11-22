from rpms.util.display import print_table


def reports_menu(report_service, log_service):
    """Menu is built from the REPORTS list, so a new report appears automatically."""
    reports = report_service.titles()
    while True:
        print("\n------ REPORTS ------")
        for number, (_, title) in enumerate(reports, start=1):
            print(f"{number}. {title}")
        print("0. Back")
        choice = input("Enter Choice: ").strip()
        if choice == "0":
            return
        try:
            if not choice.isdigit() or not 1 <= int(choice) <= len(reports):
                print("Invalid choice.")
                continue
            key = reports[int(choice) - 1][0]
            title, rows = report_service.run(key)
            print(f"\n=== {title} ===")
            print_table(list(rows[0].keys()) if rows else [], [list(r.values()) for r in rows])
            log_service.log(f"Report viewed: {title}")
        except Exception as exc:
            print("ERROR:", exc)
