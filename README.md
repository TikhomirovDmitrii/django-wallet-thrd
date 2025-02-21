# Django Wallet

A simple wallet API built with Django, SQLAlchemy, and PostgreSQL, designed to handle deposit and withdrawal operations with high concurrency (up to 1000 RPS). The project uses Docker for containerization and Locust for load testing.

## Features
- REST API for wallet operations (DEPOSIT, WITHDRAW, GET balance).
- Concurrent transaction handling using SQLAlchemy with row-level locking.
- Dockerized setup with automatic database migrations.
- Load testing with Locust to ensure performance under 1000 requests per second (RPS).
- Unit tests with `pytest` to verify API functionality.

## Tech Stack
- **Python**: 3.13
- **Django**: 5.1.6
- **SQLAlchemy**: 2.0.38
- **PostgreSQL**: 17
- **Gunicorn**: WSGI server with threading support
- **Docker**: Containerization with `docker-compose`
- **Locust**: Load testing
- **Pytest**: Unit testing

## Project Structure
django_wallet/
├── Dockerfile           
├── Dockerfile.locust   
├── docker-compose.yml 
├── requirements.txt    
├── wait-for-it.sh    
├── locustfile.py     
├── manage.py        
├── wallet_project/   
│   ├── settings.py   
│   ├── urls.py       
│   └── wsgi.py        
├── wallets/           
│   ├── admin.py     
│   ├── models.py     
│   ├── tests.py       
│   ├── urls.py         
│   └── views.py       
├── .env             
└── README.md         

## Prerequisites
- **Docker**: Install [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/).
- **Python**: 3.13 (optional, if running locally without Docker).
- **Postman**: For manual API testing (optional).

## Setup and Installation

1. Clone the Repository

git clone https://github.com/your-username/django_wallet.git
cd django_wallet

2. Configure Environment Variables
Create a .env file in the project root with the following content:

DEBUG=True
SECRET_KEY=your-secret-key-here
DB_NAME=walletdb
DB_USER=walletuser
DB_PASSWORD=walletpassword
DB_HOST=db
DB_PORT=5432

Replace your-secret-key-here with a secure key (e.g., generated via django-admin startproject).

3. Build and Run with Docker
docker-compose up --build -d
This command builds and starts the db, web, and locust services.
Migrations are applied automatically on startup of the web service.

4. Access the Application
API: http://localhost:8000/api/v1/wallets/<WALLET_UUID>/
Admin Panel: http://localhost:8000/admin/ (create a superuser with docker-compose exec web python manage.py createsuperuser)
Locust UI: http://localhost:8089/ (for load testing)
API Endpoints
Get Wallet Balance

Method: GET
URL: /api/v1/wallets/<WALLET_UUID>
Response:
json
{"balance": "5000.00"}
Errors:
404: {"error": "Wallet not found"}
Wallet Operation (Deposit/Withdraw)

Method: POST
URL: /api/v1/wallets/<WALLET_UUID>/operation
Request Body:
json
{
  "operationType": "DEPOSIT" | "WITHDRAW",
  "amount": 1000
}
Response:
json
{"status": "Success", "new_balance": "6000.00"}

Errors:
400: {"error": "Invalid or missing amount"}
400: {"error": "Invalid operationType"}
400: {"error": "Insufficient funds"}
404: {"error": "Wallet not found"}

Running Tests
Unit tests are provided to verify API functionality:
docker-compose exec web pytest
Expected output: 7 passed in X.XXs

Load Testing with Locust
Ensure a wallet exists in the database (via admin panel).
Update locustfile.py with the wallet's UUID:
self.wallet_id = "your-wallet-uuid-here"
Start Locust (if using the locust service, it's already running):
docker-compose exec web locust -f locustfile.py --host=http://localhost:8000
Open http://localhost:8089, configure:
Number of users: 1000
Spawn rate: 10
Host: http://localhost:8000
Start the test and monitor RPS (target: ~1000).
