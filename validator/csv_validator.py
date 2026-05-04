"""
CSV invoice validator.
v0.1: 4 basic rules (required fields, date format, positive amounts, duplicate IDs).
v0.2: business rules added in rules.py.
"""

import csv
from .rules import (
    rule_required_fields,
    rule_date_format,
    rule_positive_amounts,
    rule_totals_math,
    rule_due_after_issue,
    rule_valid_currency,
    rule_valid_tax_rate,
)

def rule_no_duplicate_ids(rows):
    errors = {}
    seen = {}
    for row_num, row in rows:
        inv_id = str(row.get("invoice_id", "")).strip()
        if not inv_id:
            continue
        if inv_id in seen:
            errors.setdefault(inv_id, []).append(
                f"DUPLICATE_ID | first_seen_at_row={seen[inv_id]}"
            )
        else:
            seen[inv_id] = row_num
    return errors


def validate_csv(filepath):
    """Run all active rules against a CSV file. Returns a report dict."""
    try:
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [(i + 2, row) for i, row in enumerate(reader)]
    except FileNotFoundError:
        return {"error": f"File not found: '{filepath}'"}
    except Exception as e:
        return {"error": str(e)}

    if not rows:
        return {"error": "File is empty or has no data rows."}

    all_errors = {}

    for row_num, row in rows:
        inv_id = str(row.get("invoice_id", f"row_{row_num}")).strip() or f"row_{row_num}"
        row_errors = (
            rule_required_fields(row, row_num)
            + rule_date_format(row, row_num)
            + rule_positive_amounts(row, row_num)
            + rule_totals_math(row, row_num)
            + rule_due_after_issue(row, row_num)
            + rule_valid_currency(row, row_num)
            + rule_valid_tax_rate(row, row_num)
        )
        if row_errors:
            all_errors.setdefault(inv_id, []).extend(row_errors)

    dup_errors = rule_no_duplicate_ids(rows)
    for inv_id, errs in dup_errors.items():
        all_errors.setdefault(inv_id, []).extend(errs)

    total = len(rows)

    # Contamos filas inválidas, no IDs únicos
    invalid_rows = sum(
        1 for _, row in rows
        if str(row.get("invoice_id", "")).strip() in all_errors
        or f"row_{_}" in all_errors
    )

    return {
        "filepath":  filepath,
        "format":    "csv",
        "total":     total,
        "valid":     total - invalid_rows,
        "invalid":   invalid_rows,
        "errors":    all_errors,
        "rows":      rows,
    }

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("\nUsage: python -m validator.csv_validator <file.csv>\n")
        sys.exit(1)

    report = validate_csv(sys.argv[1])

    if "error" in report:
        print(f"\n  ERROR: {report['error']}\n")
        sys.exit(1)

    sep = "─" * 60
    print(f"\n{sep}")
    print(f"  SOVOS INVOICE VALIDATOR  —  v0.1")
    print(sep)
    print(f"  File    : {report['filepath']}")
    print(f"  Total   : {report['total']} invoices")
    print(f"  Valid   : {report['valid']}")
    print(f"  Invalid : {report['invalid']}")
    print(sep)

    if not report["errors"]:
        print("\n  All invoices passed validation.\n")
    else:
        print("\n  ERRORS FOUND:\n")
        for inv_id, errors in report["errors"].items():
            for err in errors:
                error_type = err.split("|")[0].strip()
                detail     = err.split("|")[1].strip() if "|" in err else ""
                print(f"  • {inv_id:20s}  {error_type:20s}  {detail}")
        print(f"\n{sep}\n")