# Personal Finance Tracker API

A Django REST API that helps users manage their personal finances by tracking income, expenses, budgets, and savings.  

---

## Features

###User Authentication
-JWT-based login, logout.
-Registration and Password reset.
-Profile view, edit.

###Income & Expense Tracking
-Add, edit, delete transactions
-Categorize by type(food, travel, rent, etc).
-Filter by date, category, or account.
-Monthly summaries.

###Budget Planning
-Set monthly limits per category.
-Compare expenses vs budget.

###Financial Dashboard
-Total income, expenses, and net savings.
-Monthly and category stats.

###Currency Conversion
-Convert transactions to a base currency.
-Integrates with ExchangeRate API.

---

## Tech Stack
- Backend: Django, Django REST Framework
- Auth: JWT (SimpleJWT)
- Database: SQLite (default) 

---

##API Endpoints

###Authentication & User
-POST /api/register/ → Register new user
-POST /api/login/ → Obtain JWT tokens
-POST /api/token/refresh/ → Refresh token

###Accounts
-GET /api/accounts/ → List accounts
-POST /api/accounts/ → Create account
-GET /api/accounts/{id}/ → Retrieve account
-PUT /api/accounts/{id}/ → Update account
-DELETE /api/accounts/{id}/ → Delete account

---

## Setup Instructions

#Clone the repo
git clone https://github.com/CodewithJaay/finance_tracker_api.git
cd personal-finance-tracker-api

#create virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

#Install dependencies
pip install -r requirements.txt

#Apply Migrations
python manage.py makemigrations
python manage.py migrate

#Run Server
python manage.py runserver
