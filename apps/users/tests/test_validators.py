from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.users.validators import CustomValidator


class TestCustomValidator(TestCase):
    def setUp(self):
        """set up the validator instance"""
        self.validator = CustomValidator()

    def test_password_too_short(self):
        """Test that a password must be at least 8 characters"""
        with self.assertRaises(ValidationError) as cm:
            self.validator.validate('Shor1!')
        self.assertEqual(cm.exception.code, 'password_too_short')

    def test_password_no_uppercase(self):
        """Test that a password must contain at least one uppercase character"""
        with self.assertRaises(ValidationError) as cm:
            self.validator.validate('noupperpass!1')
        self.assertEqual(cm.exception.code, 'password_no_upper')

    def test_password_no_lowercase(self):
        """Test that a password must contain at least one lowercase character"""
        with self.assertRaises(ValidationError) as cm:
            self.validator.validate('NOLOWERPASS!1')
        self.assertEqual(cm.exception.code, 'password_no_lower')

    def test_password_no_numbers(self):
        """Test that a password must contain at least one number"""
        with self.assertRaises(ValidationError) as cm:
            self.validator.validate('NoNumPass!')
        self.assertEqual(cm.exception.code, 'password_no_number')

    def test_password_no_special_characters(self):
        """Test that a password must contain at least one special character"""
        with self.assertRaises(ValidationError) as cm:
            self.validator.validate('NoSpecialPass1')
        self.assertEqual(cm.exception.code, 'password_no_special')

    def test_password_valid(self):
        """Test that a password is valid"""
        try:
            self.validator.validate('ValidPassword1!')
        except ValidationError:
            self.fail('CustomValidator raised ValidationError unexpectedly!')
