"""Prints rows as a simple text table."""


def print_table(headers, rows):
    if not rows:
        print("No records found.")
        return
    text_rows = [["" if v is None else str(v) for v in row] for row in rows]
    widths = [len(h) for h in headers]
    for row in text_rows:
        for i, value in enumerate(row):
            widths[i] = max(widths[i], len(value))

    print(" | ".join(h.ljust(widths[i]) for i, h in enumerate(headers)))
    print("-+-".join("-" * w for w in widths))
    for row in text_rows:
        print(" | ".join(v.ljust(widths[i]) for i, v in enumerate(row)))
    print(f"({len(text_rows)} record(s))")
