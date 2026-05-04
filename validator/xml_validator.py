"""
XML invoice validator.
Stub — se implementa en v0.2.
"""


def validate_xml(filepath):
    """Validate a single XML invoice file. Returns a report dict."""
    return {
        "filepath": filepath,
        "total":    1,
        "valid":    0,
        "invalid":  0,
        "errors":   {},
    }