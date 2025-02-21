import uuid
from locust import HttpUser, task, between

class WalletUser(HttpUser):
    wait_time = between(0.1, 0.5)
    host = "http://web:8000"  # Указываем имя сервиса внутри Docker-сети

    def on_start(self):
        self.wallet_id = "550e8400-e29b-41d4-a716-446655440000"  # Замени на свой UUID

    @task(1)
    def get_balance(self):
        self.client.get(f"/api/v1/wallets/{self.wallet_id}")

    @task(2)
    def deposit(self):
        self.client.post(
            f"/api/v1/wallets/{self.wallet_id}/operation",
            json={"operationType": "DEPOSIT", "amount": 100},
            headers={"Content-Type": "application/json"}
        )

    @task(2)
    def withdraw(self):
        self.client.post(
            f"/api/v1/wallets/{self.wallet_id}/operation",
            json={"operationType": "WITHDRAW", "amount": 100},
            headers={"Content-Type": "application/json"}
        )
