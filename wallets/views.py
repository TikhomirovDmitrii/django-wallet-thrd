import json
import decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

db_config = settings.DATABASES['default']
DATABASE_URL = (
    f"postgresql://{db_config['USER']}:{db_config['PASSWORD']}"
    f"@{db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}"
)
logger.info(f"SQLAlchemy connecting to: {DATABASE_URL}")
engine = create_engine(DATABASE_URL, echo=False)

class Base(DeclarativeBase):
    pass

class Wallet(Base):
    __tablename__ = 'wallets'
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    balance: Mapped[decimal.Decimal] = mapped_column()

@csrf_exempt
def wallet_operation(request, wallet_id):
    logger.info(f"Processing operation for wallet_id: {wallet_id}")
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        operation_type = data.get('operationType')
        amount = data.get('amount')
        if amount is None or not isinstance(amount, (int, float)) or amount <= 0:
            return JsonResponse({'error': 'Invalid or missing amount'}, status=400)
        amount = decimal.Decimal(str(amount))

        if operation_type not in ['DEPOSIT', 'WITHDRAW']:
            return JsonResponse({'error': 'Invalid operationType'}, status=400)

    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON or missing fields'}, status=400)

    with engine.connect() as conn:
        wallet = conn.execute(
            select(Wallet).where(Wallet.id == wallet_id).with_for_update()
        ).fetchone()
        logger.info(f"Wallet found: {wallet}")

        if not wallet:
            return JsonResponse({'error': 'Wallet not found'}, status=404)

        current_balance = wallet.balance

        if operation_type == 'DEPOSIT':
            new_balance = current_balance + amount
        else:  # WITHDRAW
            if current_balance < amount:
                return JsonResponse({'error': 'Insufficient funds'}, status=400)
            new_balance = current_balance - amount

        conn.execute(
            update(Wallet).where(Wallet.id == wallet_id).values(balance=new_balance)
        )
        conn.commit()

    return JsonResponse({'status': 'Success', 'new_balance': str(new_balance)}, status=200)

def get_wallet_balance(request, wallet_id):
    logger.info(f"Getting balance for wallet_id: {wallet_id}")
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    with engine.connect() as conn:
        wallet = conn.execute(
            select(Wallet).where(Wallet.id == wallet_id)
        ).fetchone()
        logger.info(f"Wallet found: {wallet}")

        if not wallet:
            return JsonResponse({'error': 'Wallet not found'}, status=404)

    return JsonResponse({'balance': str(wallet.balance)}, status=200)
