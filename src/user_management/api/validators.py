# validators.py

from django.core.validators import RegexValidator

displayname_validator = RegexValidator(
    regex=r"^[a-zA-Z0-9_-]+$",
    message="Display name can only contain letters, digits, underscores, and hyphens."
)