from django.core.exceptions import ValidationError


class LengthValidator:
    def __init__(self, length=150):
        self.length = length

    def validate(self, password, user=None):
        if len(password) > self.length:
            raise ValidationError(
                ("Пароль должен содержать не более %(length)d символов."),
                code='password_max_length_exceeded',
                params={'length': self.length},
            )

    def get_help_text(self):
        return (
            "Ваш пароль должен содержать не более %(length)d символов."
            % {'length': self.length}
        )
