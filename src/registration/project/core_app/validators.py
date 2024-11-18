from django.core.exceptions import ValidationError
from django.utils.translation import gettext, ngettext

import re

#copied form django.contrib.auth.password_validation MinimumLengthValidator
class MyMaximumLengthValidator:
    """
    Validate that the password is of a maximum length.
    """

    def __init__(self, max_length=120):
        self.max_length = max_length

    def validate(self, password, user=None):
        if len(password) > self.max_length:
            raise ValidationError(
                ngettext(
                    "This password is too long. It must contain at most "
                    "%(max_length)d character.",
                    "This password is too long. It must contain at most "
                    "%(max_length)d characters.",
                    self.max_length,
                ),
                code="password_too_short",
                params={"max_length": self.max_length},
            )

    def get_help_text(self):
        return ngettext(
            "Your password must contain at least %(max_length)d character.",
            "Your password must contain at least %(max_length)d characters.",
            self.max_length,
        ) % {"max_length": self.max_length}
