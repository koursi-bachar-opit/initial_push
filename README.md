# SuperVision Remote Servers

A full-stack platform for renting high-performance computing (HPC) and AI/ML servers.  
Providers can list dedicated machines, and buyers can securely book compute resources.  
Built with FastAPI, PostgreSQL, Supabase Auth, Tailwind/Flowbite, pytest, and GitHub Actions CI/CD, and deployed on Render.

---

## Overview

The SuperVision Remote Servers marketplace is a fully functional HPC server-rental platform that supports:

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

See the [full repository structure](docs/coding-standards/README.md).

---

## Running the Project Locally (Docker Compose)

### Prerequisites
- Docker  
- Docker Compose  

### 1. Create your `.env` file

cp .env.example .env

### 2. Required environment variables

See [.env.example](./.env.example) for all required environment variables.

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

![CI](https://github.com/OPIT-CS/assignment-3-supervision/actions/workflows/ci.yml/badge.svg)

The CI pipeline runs on all push and pull request events targeting the `main` and `dev` branches.

### CI Workflow Steps
1. Spin up PostgreSQL service  
2. Install backend dependencies  
3. Apply Alembic migrations  
4. Run full pytest suite with coverage  
5. Enforce 80% minimum coverage  
6. Upload coverage.xml as an artifact  

Refer to the [CI/CD setup guide](docs/ci-cd-setup.md).

---

## Deployment (Render)

- Automatic deploys triggered on main branch updates
- Render PostgreSQL + web service
- Alembic migrations applied on startup
- Environment variables configured in Render Dashboard

Live site:
https://remote-servers-marketplace-test.onrender.com/

Site (provider and buyer) functionality can be tested with disposable emails provided by temp mail sites.

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
- Review summaries included in `docs/code-review-summary.md`
- PR-based workflow used for feature merges

### 4. CI/CD Pipeline
- Fully functional GitHub Actions CI
- Automated tests with coverage enforcement
- PostgreSQL service launched automatically
- Workflow located in `.github/workflows/`
- CI/CD setup details documented in `docs/ci-cd-setup.md`

---

## Combined Deliverables

### Updated Git Repository Includes:
- All implemented source code  
- Coding standards and practices  
- PR and code review history  
- CI/CD configuration  
- Stakeholder documentation