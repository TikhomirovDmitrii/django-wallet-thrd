import json
import uuid
from django.test import TransactionTestCase, Client
from wallets.models import Wallet

class WalletTests(TransactionTestCase):
    def setUp(self):
        self.client = Client()
        self.wallet = Wallet.objects.create(balance=5000.00)
        self.wallet_id = str(self.wallet.id)

    def test_get_balance_success(self):
        response = self.client.get(f'/api/v1/wallets/{self.wallet_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'balance': '5000.00'})

    def test_get_balance_not_found(self):
        fake_id = str(uuid.uuid4())
        response = self.client.get(f'/api/v1/wallets/{fake_id}')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'error': 'Wallet not found'})

    def test_deposit_success(self):
        payload = {'operationType': 'DEPOSIT', 'amount': 1000}
        response = self.client.post(
            f'/api/v1/wallets/{self.wallet_id}/operation',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'Success')
        self.assertEqual(response.json()['new_balance'], '6000.00')
        updated_wallet = Wallet.objects.get(id=self.wallet_id)
        self.assertEqual(updated_wallet.balance, 6000.00)

    def test_withdraw_success(self):
        payload = {'operationType': 'WITHDRAW', 'amount': 2000}
        response = self.client.post(
            f'/api/v1/wallets/{self.wallet_id}/operation',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'Success')
        self.assertEqual(response.json()['new_balance'], '3000.00')
        updated_wallet = Wallet.objects.get(id=self.wallet_id)
        self.assertEqual(updated_wallet.balance, 3000.00)

    def test_withdraw_insufficient_funds(self):
        payload = {'operationType': 'WITHDRAW', 'amount': 10000}
        response = self.client.post(
            f'/api/v1/wallets/{self.wallet_id}/operation',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Insufficient funds'})

    def test_invalid_json(self):
        response = self.client.post(
            f'/api/v1/wallets/{self.wallet_id}/operation',
            data='{"operationType": "DEPOSIT"}',  # Нет amount
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Invalid or missing amount'})

    def test_invalid_operation_type(self):
        payload = {'operationType': 'INVALID', 'amount': 1000}
        response = self.client.post(
            f'/api/v1/wallets/{self.wallet_id}/operation',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Invalid operationType'})
