from django.urls import path
from . import views

urlpatterns = [
    path('wallets/<uuid:wallet_id>/operation', views.wallet_operation, name='wallet_operation'),
    path('wallets/<uuid:wallet_id>', views.get_wallet_balance, name='get_wallet_balance'),
]