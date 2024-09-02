import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class CustomValidator:
    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError(
                _("Password must be at least 8 characters."),
                code='password_too_short',
            )
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("Password must contain at least one uppercase letter"),
                code='password_no_upper',
            )
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _("Password must contain at least one lowercase letter"),
                code='password_no_lower',
            )
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _("Password must contain at least one special character"),
                code='password_no_special',
            )

    def get_help_text(self):
        return _(
            "Your password must be at least 8 characters long, contain at least one uppercase letter, "
            "one lowercase letter, and one special character."
        )
