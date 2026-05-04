"""
Shared validation rules used by both CSV and XML validators.
Each rule takes a row (dict) and returns a list of error strings.
New rules for v0.2 will be added here.
"""

from datetime import datetime

REQUIRED_FIELDS = [
    "invoice_id", "issue_date", "due_date",
    "vendor_id", "vendor_name",
    "customer_id", "customer_name",
    "tax_id", "currency",
    "subtotal", "tax_rate", "tax_amount", "total",
    "status",
]

NUMERIC_FIELDS = ["subtotal", "tax_rate", "tax_amount", "total"]
DATE_FIELDS    = ["issue_date", "due_date"]
DATE_FORMAT    = "%Y-%m-%d"

# v0.2 constants (no se usan todavía)
VALID_CURRENCIES = {"ARS", "USD", "EUR"}
VALID_TAX_RATES  = {0.0, 10.5, 21.0}
MATH_TOLERANCE   = 0.02


def rule_required_fields(row, row_num):
    errors = []
    for field in REQUIRED_FIELDS:
        if field not in row or str(row[field]).strip() == "":
            errors.append(f"MISSING_FIELD | field='{field}'")
    return errors


def rule_date_format(row, row_num):
    errors = []
    for field in DATE_FIELDS:
        value = str(row.get(field, "")).strip()
        if not value:
            continue
        try:
            datetime.strptime(value, DATE_FORMAT)
        except ValueError:
            errors.append(f"INVALID_DATE | field='{field}' value='{value}'")
    return errors


def rule_positive_amounts(row, row_num):
    errors = []
    for field in NUMERIC_FIELDS:
        value = str(row.get(field, "")).strip()
        if not value:
            continue
        try:
            if float(value) < 0:
                errors.append(f"NEGATIVE_AMOUNT | field='{field}' value={value}")
        except ValueError:
            errors.append(f"INVALID_NUMBER | field='{field}' value='{value}'")
    return errors


# v0.2 rules (stubs — se implementan en el siguiente paso)

def rule_totals_math(row, row_num):
    """Rule 5: total debe ser igual a subtotal + tax_amount."""
    try:
        subtotal   = float(str(row.get("subtotal", "")).strip())
        tax_amount = float(str(row.get("tax_amount", "")).strip())
        total      = float(str(row.get("total", "")).strip())
    except ValueError:
        return []  # ya lo atrapa rule_positive_amounts

    expected = round(subtotal + tax_amount, 2)
    actual   = round(total, 2)

    if abs(expected - actual) > MATH_TOLERANCE:
        return [f"TOTAL_MISMATCH | expected={expected} actual={actual}"]
    return []


def rule_due_after_issue(row, row_num):
    """Rule 6: due_date debe ser posterior a issue_date."""
    try:
        issue = datetime.strptime(str(row.get("issue_date", "")).strip(), DATE_FORMAT)
        due   = datetime.strptime(str(row.get("due_date", "")).strip(), DATE_FORMAT)
    except ValueError:
        return []  # ya lo atrapa rule_date_format

    if due <= issue:
        return [f"DUE_BEFORE_ISSUE | issue_date={row.get('issue_date')} due_date={row.get('due_date')}"]
    return []


def rule_valid_currency(row, row_num):
    """Rule 7: currency debe estar en VALID_CURRENCIES."""
    currency = str(row.get("currency", "")).strip().upper()
    if not currency:
        return []  # ya lo atrapa rule_required_fields
    if currency not in VALID_CURRENCIES:
        return [f"INVALID_CURRENCY | value='{currency}' allowed={sorted(VALID_CURRENCIES)}"]
    return []


def rule_valid_tax_rate(row, row_num):
    """Rule 8: tax_rate debe estar en VALID_TAX_RATES."""
    value = str(row.get("tax_rate", "")).strip()
    if not value:
        return []  # ya lo atrapa rule_required_fields
    try:
        rate = float(value)
    except ValueError:
        return []  # ya lo atrapa rule_positive_amounts
    if rate not in VALID_TAX_RATES:
        return [f"INVALID_TAX_RATE | value={rate} allowed={sorted(VALID_TAX_RATES)}"]
    return []
