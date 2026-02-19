import re


def is_valid_phone(phone: str) -> bool:
    """Validate international phone number format (E.164: +XXXXXXXXXXX)."""
    pattern = r"^\+[1-9][0-9]{6,14}$"
    return bool(re.match(pattern, phone))


def is_valid_utility_reference(number: str) -> bool:
    """Basic utility/premise reference number validation."""
    return bool(number and len(number) >= 3 and number.replace("-", "").replace("/", "").isalnum())
