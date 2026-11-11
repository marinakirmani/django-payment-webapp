import json
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import Account, PaymentRequest, PaymentTransaction


def make_user(username, balance='500', currency='GBP'):
    user = User.objects.create_user(username=username, password='StrongPass123!')
    Account.objects.create(user=user, currency=currency, balance=Decimal(balance))
    return user


class SendMoneyTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.alice = make_user('alice', '500')
        self.bob = make_user('bob', '100')
        self.client.login(username='alice', password='StrongPass123!')

    def test_successful_payment(self):
        self.client.post(reverse('send_money'), {
            'recipient_username': 'bob', 'amount': '50',
        })
        self.alice.account.refresh_from_db()
        self.bob.account.refresh_from_db()
        self.assertEqual(self.alice.account.balance, Decimal('450.00'))
        self.assertEqual(self.bob.account.balance, Decimal('150.00'))
        self.assertEqual(PaymentTransaction.objects.count(), 1)

    def test_payment_to_unknown_user_does_nothing(self):
        response = self.client.post(reverse('send_money'), {
            'recipient_username': 'noone', 'amount': '50',
        })
        self.assertContains(response, 'Recipient does not exist')
        self.alice.account.refresh_from_db()
        self.assertEqual(self.alice.account.balance, Decimal('500.00'))

    def test_payment_to_self_rejected(self):
        response = self.client.post(reverse('send_money'), {
            'recipient_username': 'alice', 'amount': '50',
        })
        self.assertContains(response, 'cannot send money to yourself')

    def test_insufficient_funds(self):
        response = self.client.post(reverse('send_money'), {
            'recipient_username': 'bob', 'amount': '1000',
        })
        self.assertContains(response, 'Insufficient funds')
        self.assertEqual(PaymentTransaction.objects.count(), 0)
        self.alice.account.refresh_from_db()
        self.assertEqual(self.alice.account.balance, Decimal('500.00'))


class PaymentRequestTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.alice = make_user('alice', '500')
        self.bob = make_user('bob', '500')

    def test_request_creates_pending_request(self):
        self.client.login(username='alice', password='StrongPass123!')
        self.client.post(reverse('request_money'), {
            'requested_from_username': 'bob', 'amount': '50',
        })
        req = PaymentRequest.objects.get()
        self.assertEqual(req.status, 'Pending')
        self.assertEqual(req.amount, Decimal('50.00'))

    def test_pay_request_transfers_funds(self):
        req = PaymentRequest.objects.create(
            requester=self.alice, requested_from=self.bob,
            amount=Decimal('50'), status='Pending',
        )
        self.client.login(username='bob', password='StrongPass123!')
        self.client.post(reverse('pay_request', args=[req.id]))
        req.refresh_from_db()
        self.assertEqual(req.status, 'Paid')
        self.alice.account.refresh_from_db()
        self.bob.account.refresh_from_db()
        self.assertEqual(self.alice.account.balance, Decimal('550.00'))
        self.assertEqual(self.bob.account.balance, Decimal('450.00'))

    def test_reject_request_marks_rejected(self):
        req = PaymentRequest.objects.create(
            requester=self.alice, requested_from=self.bob,
            amount=Decimal('50'), status='Pending',
        )
        self.client.login(username='bob', password='StrongPass123!')
        self.client.post(reverse('reject_request', args=[req.id]))
        req.refresh_from_db()
        self.assertEqual(req.status, 'Rejected')
        self.alice.account.refresh_from_db()
        self.assertEqual(self.alice.account.balance, Decimal('500.00'))


class AccessControlTests(TestCase):

    def setUp(self):
        self.client = Client()
        make_user('alice', '500')

    def test_anonymous_redirected_from_send_money(self):
        response = self.client.get(reverse('send_money'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)

    def test_regular_user_cannot_view_admin_accounts(self):
        self.client.login(username='alice', password='StrongPass123!')
        response = self.client.get(reverse('admin_accounts'))
        self.assertEqual(response.status_code, 302)


class ConversionServiceTests(TestCase):

    def test_supported_conversion_returns_200(self):
        response = self.client.get('/webapps2026/conversion/GBP/USD/100/')
        self.assertEqual(response.status_code, 200)
        body = json.loads(response.content)
        self.assertEqual(body['from_currency'], 'GBP')
        self.assertEqual(body['to_currency'], 'USD')

    def test_unsupported_currency_returns_400(self):
        response = self.client.get('/webapps2026/conversion/GBP/XYZ/100/')
        self.assertEqual(response.status_code, 400)

    def test_only_get_is_allowed(self):
        response = self.client.post('/webapps2026/conversion/GBP/USD/100/')
        self.assertEqual(response.status_code, 405)
