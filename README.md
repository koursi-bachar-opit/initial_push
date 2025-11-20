# Remote Servers Marketplace
![CI](https://github.com/OPIT-CS/assignment-3-supervision/actions/workflows/ci.yml/badge.svg)

A full-stack platform for renting high-performance computing (HPC) and AI/ML servers.  
Providers can list dedicated machines, and buyers can securely book compute resources.  
Built with FastAPI, PostgreSQL, Supabase Auth, Tailwind/Flowbite, pytest, and GitHub Actions CI/CD, and deployed on Render.

---

## Live Deployment
https://remote-servers-marketplace-test.onrender.com/

---

## Overview

Remote Servers Marketplace is a fully functional HPC server-rental platform that supports:

- Provider onboarding and server listings
- Secure authentication via Supabase JWT (HS256) stored in HTTP-only cookies
- Booking workflows for buyers (request → confirm → start → end → cancel)
- Role-based access control for providers, buyers, and admins
- A responsive frontend served with Jinja2 Templates, TailwindCSS, and Flowbite
- Automated testing and CI integration with coverage enforcement

---

## Tech Stack

### Backend
- FastAPI (Python 3.12)
- PostgreSQL (SQLAlchemy ORM)
- Alembic migrations
- Supabase Auth (Legacy HS256 JWT)
- Jinja2 template rendering
- pytest (unit + integration tests)

### Frontend
- TailwindCSS
- Flowbite UI components
- HTML/Jinja2 + JavaScript (fetch API)

### DevOps / Tooling
- Docker & Docker Compose
- GitHub Actions CI
- Render Web Services deployment
- Coverage reports and artifact uploads

---

## Features

### Authentication and Authorization
- Supabase-managed signup, login, logout
- JWT stored in HTTP-only cookies
- Role-based access protection (`require_roles`)
- Automatic validation on every request

### Provider Features
- Create and manage server listings
- Register dedicated machines
- View provider-specific bookings
- Confirm, start, end customer bookings

### Buyer Features
- Browse all server listings
- Request a booking
- View current and past bookings
- Cancel pending bookings

### General Features
- Fully responsive UI (Tailwind/Flowbite)
- Dynamic role-based template rendering
- Dark mode support
- Health endpoint `/api/v1/health`
- Inline API documentation via FastAPI docs:  
  https://remote-servers-marketplace-test.onrender.com/docs

---

## Project Structure

```
assignment-3-supervision/
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── alembic/
│   ├── versions/
│   │   └── 017509d8e5d3_initial_schema.py
│   ├── env.py
│   ├── README
│   └── script.py.mako
│
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── bookings.py
│   │   ├── listings.py
│   │   └── machines.py
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── booking_repository.py
│   │   ├── listing_repository.py
│   │   ├── machine_repository.py
│   │   └── user_repository.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── bookings_service.py
│   │   └── listings_service.py
│   │
│   ├── __init__.py
│   ├── auth.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
│
├── docs/
│   ├── architecture.md
│   ├── coding-standards.md
│   ├── implementation-patterns.md
│   └── README.md
│
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   │       ├── api.js
│   │       ├── auth.js
│   │       ├── bookings.js
│   │       ├── dashboard.js
│   │       ├── listings.js
│   │       ├── login.js
│   │       ├── signup.js
│   │       └── supabaseClient.js
│   │
│   └── templates/
│       ├── base.html
│       ├── bookings.html
│       ├── dashboard.html
│       ├── index.html
│       ├── listings.html
│       ├── login.html
│       └── signup.html
│
├── tests/
│   ├── e2e/
│   │
│   ├── factories/
│   │   ├── bookings.py
│   │   ├── listings.py
│   │   ├── machines.py
│   │   └── users.py
│   │
│   ├── integration/
│   │   └── api/
│   │       ├── test_api_booking_lifecycle.py
│   │       ├── test_api_bookings.py
│   │       ├── test_api_listings.py
│   │       ├── test_api_machines.py
│   │       ├── test_auth_api.py
│   │       └── test_health_endpoint.py
│   ├── performance/
│   ├── regression/
│   ├── unit/
│   │   └── auth/
│   │       ├── test_auth_internal.py
│   │       └── test_db_lifecycle.py
│   │
│   ├── assertions.py
│   ├── conftest.py
│   ├── test_config.py
│   └── test_helpers.py
│
├── .coverage
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── coverage.xml
├── docker-compose.yml
├── Dockerfile
├── pytest.ini
├── README.md
└── requirements.txt
```

---

## Running the Project Locally (Docker Compose)

### Prerequisites
- Docker  
- Docker Compose  

### 1. Create your `.env` file

cp .env.example .env

### 2. Required environment variables

```
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
DATABASE_URL=
TEST_DATABASE_URL=
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_JWT_SECRET=
```

### 3. Start the stack

docker compose up --build


This launches:
- web — FastAPI backend + frontend (port 8000)
- mock_pg — PostgreSQL 16 with healthcheck and volume persistence

### 4. Apply migrations

docker compose exec web alembic upgrade head


The app is now available at:

http://localhost:8000

---

## Testing

The test suite includes unit tests and integration tests.

### What is covered
- Authentication validation
- SQLAlchemy session lifecycle
- Listings API
- Machines API
- Full booking lifecycle
- Provider, buyer, and admin roles

### Test Database
- Uses TEST_DATABASE_URL
- Alembic migrations applied automatically
- Each test runs inside its own rolled-back transaction

### Run tests manually

pytest --cov=app

---

## CI/CD Pipeline (GitHub Actions)

The CI pipeline runs on all push and pull request events targeting the `main` and `dev` branches.

### CI Workflow Steps
1. Spin up PostgreSQL service  
2. Install backend dependencies  
3. Apply Alembic migrations  
4. Run full pytest suite with coverage  
5. Enforce 80% minimum coverage  
6. Upload coverage.xml as an artifact  

The CI badge is shown at the top of this README.

---

## Deployment (Render)

- Automatic deploys triggered on main branch updates
- Render PostgreSQL + web service
- Alembic migrations applied on startup
- Environment variables configured in Render Dashboard

Live site:  
https://remote-servers-marketplace-test.onrender.com/

---

## Additional Documentation (docs/ folder)

The `docs/` directory includes:

- Stakeholder feedback document and UAT report
- Coding standards and practices  
- Code review summaries  
- CI/CD setup details  

---

# Course Deliverables Mapping (For Grading)

Below is a section that demonstrates fulfilment of the project rubric. This section is intentionally separated to maintain industry-standard documentation above.

---

## Stakeholders

### 1. Stakeholder Testing Feedback
- Located in `docs/stakeholder-testing/`
- Includes screenshots, notes, and a summary report
- Demonstrates that implemented features meet user needs

---

## Developers

### 1. Source Code Repository
- Frequent commits and clear commit messages
- Branch usage: feature/system-refactor, docs, and others used earlier in development
- PR created with reviewer comments

### 2. Feature Implementation
- Implemented signup, login, machine creation, machine creation, and full booking lifecycle
- Role-based dashboards
- Pydantic validation and service-layer architecture
- Coding standards documented in `docs/coding-standards/`

### 3. Pull Requests and Code Reviews
- Latest PR includes reviewer comments
- Review summaries included in `code-review-summary.md`
- PR-based workflow used for feature merges

### 4. CI/CD Pipeline
- Fully functional GitHub Actions CI
- Automated tests with coverage enforcement
- PostgreSQL service launched automatically
- Workflow located in `.github/workflows/`
- CI/CD setup details documented in `ci-cd-setup.md`

---

## Combined Deliverables

### Updated Git Repository Includes:
- All implemented source code  
- Coding standards and practices  
- PR and code review history  
- CI/CD configuration  
- Stakeholder documentation