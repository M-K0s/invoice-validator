"""
System prompts and prompt builders for the AI Assistant.
"""


SYSTEM_PROMPT = """You are an expert technical consultant assistant at Sovos, 
a global tax compliance software company. You help implementation consultants 
during customer onboarding and ERP integrations.

You have deep knowledge of:
- Invoice validation rules and compliance requirements
- ERP systems (SAP, Oracle, Microsoft Dynamics) and their data exports
- Tax regulations in Latin America, especially Argentina (AFIP), Brazil, and Mexico
- Data formats: CSV, XML, JSON
- Common data quality issues in invoice processing

Your role is to:
1. Explain validation errors in simple, actionable terms
2. Suggest how to fix issues in the source ERP system
3. Answer questions about compliance rules and best practices
4. Help consultants understand patterns in validation results

Always be concise, practical, and professional. Respond in the same language 
the user writes in. If they write in Spanish, respond in Spanish."""


def build_context_prompt(report):
    """Build a prompt with the current validation report as context."""
    if not report:
        return ""

    lines = [
        "CURRENT VALIDATION REPORT CONTEXT:",
        f"- File: {report.get('filepath', 'unknown')}",
        f"- Total invoices: {report.get('total', 0)}",
        f"- Valid: {report.get('valid', 0)}",
        f"- Invalid: {report.get('invalid', 0)}",
    ]

    if report.get("errors"):
        lines.append("- Errors found:")
        error_counts = {}
        for errors in report["errors"].values():
            for err in errors:
                error_type = err.split("|")[0].strip()
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
        for error_type, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  • {error_type}: {count} occurrence(s)")

    return "\n".join(lines)