from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from payapp.models import Account



class RegistrationTests(TestCase):

    def test_register_creates_gbp_account_with_500(self):
        response = self.client.post(reverse('register'), {
            'username': 'alice',
            'first_name': 'Alice',
            'last_name': 'Smith',
            'email': 'alice@example.com',
            'currency': 'GBP',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='alice')
        account = Account.objects.get(user=user)
        self.assertEqual(account.currency, 'GBP')
        self.assertEqual(account.balance, Decimal('500.00'))

    def test_register_creates_usd_account_with_converted_balance(self):
        response = self.client.post(reverse('register'), {
            'username': 'bob',
            'first_name': 'Bob',
            'last_name': 'Jones',
            'email': 'bob@example.com',
            'currency': 'USD',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, 302)
        account = Account.objects.get(user__username='bob')
        self.assertEqual(account.currency, 'USD')
        self.assertGreater(account.balance, Decimal('640'))
        self.assertLess(account.balance, Decimal('660'))


class LoginLogoutTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='charlie', password='StrongPass123!',
        )
        Account.objects.create(user=self.user, currency='GBP', balance=Decimal('500'))

    def test_invalid_login_shows_error(self):
        response = self.client.post(reverse('login'), {
            'username': 'charlie', 'password': 'wrong',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')

    def test_valid_login_redirects_to_home(self):
        response = self.client.post(reverse('login'), {
            'username': 'charlie', 'password': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, 302)
