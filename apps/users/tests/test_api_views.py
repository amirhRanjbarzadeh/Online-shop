from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from unittest.mock import patch
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class RequestCodeViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('users-api:request-code')
        self.email = 'testuser@example.com'

    @patch('random.randint')
    @patch('django.core.mail.send_mail')
    def test_post_valid_email(self, mock_send_mail, mock_randint):
        mock_randint.side_effect = [1, 2, 3, 4, 5, 6, 7, 8]
        data = {'email': self.email}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=self.email).exists())
        user = User.objects.get(email=self.email)
        self.assertFalse(user.is_active)
        self.assertTrue(user.check_password('12345678'))

    def test_post_invalid_email(self):
        data = {'email': 'invalid-email'}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email='invalid-email').exists())


class CodeVerificationViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('users-api:verify-code')
        self.email = 'testuser@example.com'
        self.user = User.objects.create(email=self.email)
        self.user.set_password('12345678')
        self.user.code_created_at = timezone.now()
        self.user.save()

    def test_post_valid_code_existing_user(self):
        data = {'email': self.email, 'code': '12345678'}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
        self.assertEqual(response.data['message'], "Login successful, redirecting to home")

    def test_post_valid_code_new_user(self):
        self.user.is_active = False
        self.user.save()

        data = {'email': self.email, 'code': '12345678'}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "New user, redirecting to signup.")

    def test_post_invalid_code(self):
        data = {'email': self.email, 'code': '87654321'}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid email or code.')

    def test_post_expired_code(self):
        self.user.code_created_at = timezone.now() - timezone.timedelta(minutes=3)
        self.user.save()

        data = {'email': self.email, 'code': '12345678'}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'The code has expired. Please request a new code.')

    def test_post_invalid_email(self):
        data = {'email': 'wrongemail@example.com', 'code': '12345678'}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid email or code.')


class SignUpViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('users-api:sign-up')
        self.email = 'testuser@example.com'
        self.user = User.objects.create(email=self.email, is_active=False)
        self.user.set_password("12345678")
        self.user.save()

    def test_post_user_does_not_exist(self):
        non_existent_email = 'nonexistent@example.com'
        data = {"email": non_existent_email}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'User does not exist.')

    def test_post_user_already_active(self):
        self.user.is_active = True
        self.user.save()

        data = {'email': self.email}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'User is already active.')

    @patch('rest_framework_simplejwt.tokens.RefreshToken.for_user')
    def test_post_successful_signup(self, mock_for_user):
        mock_for_user.return_value = RefreshToken()
        data = {
            'email': self.email,
            'password': 'newpassword123',
            'first_name': 'Test',
            'last_name': 'User'
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()  # Refresh user from the database

        # Check if user is active now
        self.assertTrue(self.user.is_active)

        # Check if the serializer's save method worked
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')

        # Check if tokens are returned
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
        self.assertEqual(response.data['message'], "Login successful, redirecting to home")

