# Django Payment Web Application

**University of Sussex — academic software development project**

A Django-based web application demonstrating account registration, authentication, simulated payments, payment requests and transaction history. Includes a separate currency-conversion endpoint, administrative views and automated tests.

> **Educational demonstration only.** This is not a banking application: payments use simulated balances, and exchange rates are fixed sample values. It is not intended to handle real money or production users.

## Features

- Register and log in using Django authentication.
- Create an account with an initial simulated balance.
- Send simulated payments between registered user accounts, with balance checks and transaction records.
- Request a payment from another registered user, then pay or reject the request.
- View sent and received transactions and payment requests.
- Convert between GBP, USD and EUR using static example rates through a JSON endpoint.
- Access administrative account, transaction and admin-user management views (superusers only).
- Exercise application behaviour with Django automated tests.

## Technologies

Python · Django 4.2 · HTML · Bootstrap 5 · SQLite (local development) · Django test framework · requests

I also deployed and tested a Django application on an **AWS EC2 Ubuntu instance** as part of my university work. Cloud credentials, server configuration and private keys are intentionally **not included** in this repository.

## Getting started

### Requirements

- Python 3.10 or newer (compatible with the pinned Django 4.2 series)
- A terminal (macOS, Linux or Windows)

### 1. Set up a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate with `.venv\Scripts\activate` and use `py` if `python3` is unavailable.

### 2. Initialise the database

```bash
python manage.py migrate
```

Optionally, create an admin account with your own strong password:

```bash
python manage.py createsuperuser
```

### 3. Start the app

```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000/webapps2026/** in your browser. Register two accounts to try sending payments and requesting payments between them.

### 4. Run the tests

```bash
python manage.py test
```

The repository includes tests of registration, authentication, payments, payment requests, access restrictions and currency conversion. Test execution depends on installing the listed dependencies.

## Main folders

```text
webapps2026/     Django project configuration
register/        Registration, authentication and account creation
payapp/          Payment and payment-request features and tests
conversion/      Example currency conversion endpoint
templates/       HTML templates
manage.py        Django management command entry point
requirements.txt Pinned Python dependencies
```

## Configuration and security

- The original local database, TLS private key and certificate are **not included**.
- A hard-coded test admin account in the original coursework version was removed. Create a superuser using Django's command instead.
- The application secret key is read from `DJANGO_SECRET_KEY`, or generated temporarily for local development. Set a strong key when deploying.
- `DJANGO_DEBUG` defaults to `true` **for local development only**. Set it to `false` for deployment.
- `DJANGO_ALLOWED_HOSTS` defaults to `localhost,127.0.0.1`; configure it for your own deployment host.
- This is an academic portfolio project, **not a production-ready payments service**. Security and deployment hardening are required before any real-world use.

See [SECURITY_NOTES.md](SECURITY_NOTES.md) for a record of public-sharing changes.
