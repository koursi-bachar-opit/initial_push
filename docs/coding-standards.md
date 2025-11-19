# Coding Standards and Practices

> **Quick Start**: New to the codebase? Start with [Code Organization](#code-organization) and [Naming Conventions](#naming-conventions). Need examples? See [Implementation Patterns](./implementation-patterns.md).

This document outlines the coding standards, architectural patterns, and best practices followed during the implementation of the Remote Servers Marketplace API.

## Quick Reference

| Topic                 | Key Rule                                          | See Section                                                      |
| --------------------- | ------------------------------------------------- | ---------------------------------------------------------------- |
| **File naming**       | `snake_case.py`                                   | [Naming Conventions](#naming-conventions)                        |
| **Class naming**      | `PascalCase`                                      | [Naming Conventions](#naming-conventions)                        |
| **Function naming**   | `snake_case()`                                    | [Naming Conventions](#naming-conventions)                        |
| **Error handling**    | `ValueError` in services → `HTTPException` in API | [Error Handling](#error-handling)                                |
| **Database sessions** | Use `get_db()` dependency                         | [Database Patterns](#database-patterns)                          |
| **Authentication**    | `require_roles("provider", "admin")`              | [Authentication & Authorization](#authentication--authorization) |

## Table of Contents

1. [Project Architecture](#project-architecture)
2. [Code Organization](#code-organization)
3. [Naming Conventions](#naming-conventions)
4. [API Design Patterns](#api-design-patterns)
5. [Database Patterns](#database-patterns)
6. [Error Handling](#error-handling)
7. [Authentication & Authorization](#authentication--authorization)
8. [Testing Practices](#testing-practices)
9. [Configuration Management](#configuration-management)
10. [Documentation Standards](#documentation-standards)

---

## Project Architecture

### Layered Architecture

The project follows (with light modular monolith characteristics for future refactors) a **layered architecture** pattern with clear separation of concerns:

```
┌──────────────────────────────┐
│ API Layer (endpoints)        │  ← HTTP endpoints, request/response handling
│ app/api/                     │
├──────────────────────────────┤
│ Schemas (Pydantic DTOs)      │  ← Pydantic validation schemas
│ app/schemas.py               │
├──────────────────────────────┤
│ Service Layer (business)     │  ← Business rules, workflow orchestration
│ app/services/                │
├──────────────────────────────┤
│ Repository Layer (DB access) │  ← Database operations, data access
│ app/repositories/            │
├──────────────────────────────┤
│ Models Layer (ORM)           │  ← SQLAlchemy ORM models
│ app/models.py                │
└──────────────────────────────┘
```

### Key Principles

-  **Separation of Concerns**: Each layer has a distinct responsibility
-  **Dependency Injection**: FastAPI's dependency system used throughout
-  **Single Responsibility**: Each module/function has one clear purpose
-  **DRY (Don't Repeat Yourself)**: Shared logic extracted to reusable functions


---

## Code Organization

### Directory Structure

```
app/ 
├── api/
│   ├── __init__.py
│   ├── bookings.py
│   ├── listings.py
│   ├── machines.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── booking_repository.py
│   │   ├── listing_repository.py
│   │   │   ├── machine_repository.py
│   │   └── user_repository.py
│   └── services/
│       ├── __init__.py
│       ├── bookings_service.py
│       └── listings_service.py
├── __init__.py
├── auth.py
├── config.py
├── database.py
├── main.py
├── models.py
└── schemas.py
```

### Module Organization Principles

1. **API Routes** (`app/api/`): Thin controllers that handle HTTP concerns

   - Route definitions
   - Request/response models
   - Dependency injection for auth and DB
   - Error handling at HTTP level

2. **Services** (`app/services/`): Business logic and workflows

   - Complex business rules
   - State transitions (e.g., booking lifecycle)
   - Cross-model operations
   - Validation beyond schema validation


   - Basic create, read, update, delete
   - Query building
   - Direct model manipulation

4. **Models** (`app/models.py`): Database schema definitions

   - SQLAlchemy ORM models
   - Relationships and constraints
   - Enum definitions for status fields

5. **Schemas** (`app/schemas.py`): Data validation and serialization
   - Pydantic models for request/response
   - Field validation rules
   - Type conversions

---

## Naming Conventions

### Files and Modules

-  **Snake_case** for all Python files: `bookings_service.py`, `test_auth.py`
-  **Descriptive names**: Files should clearly indicate their purpose
-  **Plural for collections**: `listings.py`, `bookings.py` (API routes)

**Examples:**

```python
#  Good
bookings_service.py
test_api_booking_lifecycle.py

#  Bad
service.py
test1.py
```

### Classes

-  **PascalCase**: `Listing`, `Booking`, `BookingStatus`, `Settings`
-  **Descriptive nouns**: Classes represent entities or concepts
-  **Suffix conventions**:
  - **Models**: `Listing`, `Booking` (no suffix)
  - **Schemas**: `ListingCreate`, `ListingRead`, `BookingCreate` (action suffix)
  - **Enums**: `BookingStatus` (descriptive name)

**Examples:**

```python
#  Good
class Listing(Base): ...
class ListingCreate(BaseModel): ...
class BookingStatus(str, Enum): ...

#  Bad
class listing(Base): ...
class CreateListing(BaseModel): ...
```

### Functions and Variables

-  **snake_case**: `create_booking()`, `get_listings()`, `buyer_name`
-  **Verbs for functions**: `create_`, `get_`, `list_`, `update_`, `delete_`
-  **Nouns for variables**: `booking_id`, `listing`, `db_session`

**Examples:**

```python
#  Good
def create_booking(...): ...
def get_listings(...): ...
booking_id = 123

#  Bad
def CreateBooking(...): ...
def getListings(...): ...
bookingId = 123
```

### Constants

- **UPPER_SNAKE_CASE**: `DATABASE_URL`, `SUPABASE_JWT_PUBLIC_KEY`
- Used for configuration values and environment variables

### Database Tables

- **Plural, lowercase**: `listings`, `bookings`
- **Snake_case** for column names: `buyer_user_id`, `start_time`, `active_session_start`

---

## API Design Patterns

### RESTful Endpoints

The API follows REST principles:

- **Resource-based URLs**: `/api/v1/listings`, `/api/v1/bookings`, `/api/v1/machines`
- **HTTP methods**: GET (read), POST (create), PUT (update), DELETE (remove)
- **Status codes**: 200 (success), 201 (created), 400 (bad request), 404 (not found), 409 (conflict)

### Endpoint Structure

```python
@router.post(
    "/",
    response_model=schemas.ListingRead,
    status_code=201,
    dependencies=[Depends(require_roles(models.UserRole.PROVIDER, models.UserRole.ADMIN))],
)
def create_listing(
    listing: schemas.ListingCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """
    Create a new listing.
    Only providers and admins are allowed this function.
    """
    return listings_service.create_listing(db, user.id, listing)
```

**Pattern Elements:**

- **Route decorator**: Defines HTTP method, path, response model, status code
- **Dependencies**: Authentication/authorization via `Depends()`
- **Type hints**: All parameters and return types explicitly typed
- **Docstrings**: Clear description of endpoint purpose and behavior
- **Response models**: Pydantic schemas ensure consistent API responses

### API Versioning

- **URL-based versioning**: `/api/v1/` prefix
- Allows for future API versions without breaking existing clients

### Request/Response Models

- **Request schemas**: Inherit from `BaseModel`, define input validation
- **Response schemas**: Inherit from request schemas, add `id` and computed fields
- **ConfigDict**: Used for ORM mode (`from_attributes=True`) to serialize SQLAlchemy models

Example:

```python
class ListingCreate(BaseModel):
    """Payload sent by providers or admins when creating a new listing."""
    machine_id: int
    title: str = Field(min_length=1)
    price: float = Field(ge=0)

class ListingRead(ListingCreate):
    id: int
    machine: Optional[MachineRead] = None
    model_config = ConfigDict(from_attributes=True)
```

---

## Database Patterns

### SQLAlchemy ORM Usage

**Model Definition Pattern:**

```python
class Listing(Base):
    """
    A listing is something a provider offers for rent.
    For example, a VM, GPU instance, or small compute server.
    Buyers can browse listings and book them for a time window.
    """
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)

    #The listing links to the underlying machine being rented
    machine_id = Column(
        Integer,
        ForeignKey("machines.id", ondelete="CASCADE"),
        nullable=False,
    )

    title = Column(String, nullable=False)
    price = Column(Float, nullable=False)

    #Listing has cardinal relationships to machine and bookings
    machine = relationship("Machine", back_populates="listings")
    bookings = relationship("Booking", back_populates="listing")
```

**Key Practices:**

- **Table names**: Explicit `__tablename__` for clarity
- **Docstrings**: Every model has a descriptive docstring
- **Indexes**: Primary keys automatically indexed
- **Relationships**: Defined with `relationship()` and `back_populates`
- **Foreign keys**: Explicit `ForeignKey` with cascade rules (`ondelete="CASCADE"`)

### Enum Handling

**Database Enums:**

- Stored as VARCHAR (non-native enum) for portability
- Defined in `models.py` as Python `Enum` classes
- Mirrored in `schemas.py` for API validation

```python
class BookingStatus(str, Enum):
    REQUESTED = "requested"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
```

### Session Management

**Dependency Injection Pattern:**

```python
def get_db():
    """
    The FastAPI dependency for providing a scoped database session.
    Ensures that the session is closed after request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Practices:**

- **Context manager**: `try/finally` ensures cleanup
- **Per-request sessions**: Each HTTP request gets its own session
- **Explicit commits**: `db.commit()` called after mutations
- **Refresh after commit**: `db.refresh(obj)` to reload from DB

### Database Migrations

- **Alembic** used for schema versioning
- **Migration files**: Descriptive revision IDs and comments
- **Upgrade/downgrade**: Both directions supported for rollback capability

---

## Error Handling

### HTTP Exception Pattern

**Service Layer:**

```python
if not listing:
    raise ValueError("Listing not found")
```

**API Layer:**

```python
try:
    return bookings_service.request_booking(...)
except ValueError as e:
    raise HTTPException(status_code=404, detail=str(e))
```

### Error Handling Strategy

**Three-layer approach:**

1. **Service Layer**: Raises `ValueError` for business logic errors
2. **Service Layer**: Raises `HTTPException` for HTTP-specific errors (status codes, conflicts)
3. **API Layer**: Catches `ValueError` and converts to appropriate HTTP status
4. **API Layer**: Allows `HTTPException` to bubble up unchanged


### Status Code Conventions

| Code    | Meaning               | When to Use                                                   |
| ------- | --------------------- | ------------------------------------------------------------- |
| **200** | OK                    | Successful GET/PUT/DELETE                                     |
| **201** | Created               | Successful POST (resource created)                            |
| **400** | Bad Request           | Invalid input data or business rule violation                 |
| **401** | Unauthorized          | Missing or invalid authentication token                       |
| **403** | Forbidden             | Authenticated but insufficient permissions                    |
| **404** | Not Found             | Resource doesn't exist                                        |
| **409** | Conflict              | State conflict (e.g., trying to start already-active session) |
| **500** | Internal Server Error | Unexpected server errors                                      |

### Error Messages

- **Descriptive**: Clear explanation of what went wrong
- **User-friendly**: Avoid exposing internal implementation details
- **Consistent format**: All errors return `{"detail": "message"}`

---

## Authentication & Authorization

### Token-Based Authentication

**Dual-Mode Support:**

1. **Production**: JWT tokens from Supabase (RS256)
2. **Development/Testing**: Mock tokens (`role:username` format)

**Implementation Pattern:**

```python
def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    """
    1. Check the Bearer header (Supabase uses it)
    2. If no header, use cookie.
    3. If token has "role:email" format, consider as mock local creds
    4. Otherwise, decode the real JWT
    """
    token = None

    if creds:
        token = creds.credentials.strip()

    elif access_token:
        token = access_token

    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    if ":" in token:
        return _parse_mock_token_and_create_user(db, token)

    if token.count(".") != 2:
        raise HTTPException(status_code=401, detail="Invalid bearer token")

    decoded = _decode_supabase_jwt(token)
    sub = decoded.get("sub")
    email = decoded.get("email") or decoded.get("user_metadata", {}).get("email")

    if not sub or not email:
        raise HTTPException(status_code=401, detail="Invalid JWT payload")

    metadata = decoded.get("user_metadata") or {}
    role = metadata.get("role")

    return _get_or_create_user(db, sub, email, role)
```

### Role-Based Access Control

**Factory Pattern for Role Requirements:**

```python
def require_roles(*allowed: models.UserRole):
    """Use this dependency to protect routes so only certain roles can reach them."""
    def dep(user: models.User = Depends(get_current_user)):
        if user.role not in allowed:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user

    return dep
```

**Usage:**

```python
@router.post(
    "/",
    response_model=schemas.ListingRead,
    status_code=201,
    dependencies=[Depends(require_roles(models.UserRole.PROVIDER, models.UserRole.ADMIN))],
)
def create_listing(...):
    ...
```

### Roles

- **buyer**: Can request bookings, view listings
- **provider**: Can create listings, confirm bookings, manage sessions
- **admin**: Full access to all operations
- **org_admin**: Organization-level admin (if needed)

---

## Testing Practices

### Test Organization

**Test Structure:**

```
tests/
├── e2e/
├── factories/
│   ├── bookings.py
│   ├── listings.py
│   ├── machines.py
│   └── users.py
├── functional/
│   └── api/
│       ├── test_api_booking_lifecycle.py
│       ├── test_api_bookings.py
│       ├── test_api_listings.py
│       ├── test_api_machines.py
│       ├── test_auth_api.py
│       └── test_health_endpoint.py
├── integration/
├── performance/
├── regression/
└── unit/
    ├── auth/
    │   └── test_auth_internal.py
    ├── test_db_lifecycle.py
    ├── assertions.py
    ├── conftest.py
    ├── test_config.py
    └── test_helpers.py
```

### Test Fixtures

**Database Setup:**

```python
@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    command.upgrade(alembic_cfg, "head")
    yield

@pytest.fixture()
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()
```

**Practices:**

- **Session-scoped migrations**: Run once before all tests
- **Transaction isolation**: Each test gets a fresh transaction that rolls back
- **Dependency override**: FastAPI's `get_db` overridden for testing
- **Test client**: FastAPI's `TestClient` for HTTP endpoint testing

### Test Markers

**Markers defined in `pytest.ini`:**

- `integration`: Marks tests that require database/external services

### Test Coverage

- **Coverage reporting**: Configured via `pytest-cov`
- **Coverage targets**: Aim for 80% total coverage, high coverage of business logic

### Testing Patterns

1. **Arrange-Act-Assert**: Clear test structure
2. **Descriptive names**: Test names describe what they test
3. **Isolation**: Each test is independent
4. **Mock tokens**: Use `Bearer role:username` format for auth in tests

---

## Configuration Management

### Settings Class Pattern

**Centralized Configuration:**

```python
class Settings(BaseSettings):
    """This class defines every setting our backend needs.
    Pydantic automatically loads them from the environment (such as Github secrets),
    .env files, or Docker env vars. This way, we avoid hard-coded secrets and keep configuration centralized."""

    model_config = ConfigDict(
        env_file=".env",      
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )

    ENV: str = Field(default="local")
    DATABASE_URL: str | None = None
    TEST_DATABASE_URL: str | None = None
    ...
```

**Practices:**

- **Pydantic Settings**: Type-safe configuration with validation
- **Environment variables**: Primary source of configuration
- **Default values**: Sensible defaults for local development
- **Case sensitivity**: Environment variable names are case-sensitive
- **Singleton pattern**: `settings = Settings()` instance shared across app

### Environment Variables

- **Local development**: `.env` file (gitignored)
- **CI/CD**: GitHub Secrets injected as environment variables
- **Production**: Environment variables set by deployment platform

---

## Documentation Standards

### Code Documentation

**Module-Level Docstrings:**

```python
"""
This service defines how bookings behave, including they move from REQUESTED,
to CONFIRMED, become ACTIVE, and then COMPLETE or CANCELLED.

The router calls into this layer whenever the user tries to perform
an action. The repository only reads/writes to the DB. The rules
for what is allowed live here.
"""
```

**Function Docstrings:**

```python
def request_booking(db: Session, listing_id: int, buyer_user_id: int, start_time: datetime, end_time: datetime):
    """
    This is the flow buyers use when they request a booking.
    We calculate the estimated price up front so the buyer can
    preview what they'll pay, but the final billing happens once the
    active session ends.
    """
```

**Class Docstrings:**

```python
class Listing(Base):
    """
    A listing is something a provider offers for rent.
    For example, a VM, GPU instance, or small compute server.
    Buyers can browse listings and book them for a time window.
    """
```

### Documentation Practices

1. **All public functions**: Have docstrings explaining purpose and behavior
2. **Complex logic**: Step-by-step explanations in docstrings
3. **Parameters**: Type hints serve as parameter documentation
4. **Return values**: Type hints indicate return types
5. **Edge cases**: Documented in docstrings or comments

### Inline Comments

- **Why, not what**: Comments explain reasoning, not obvious code
- **Business logic**: Complex calculations explained
- **Workarounds**: Temporary solutions or known issues documented

---

## Additional Best Practices

### Type Hints

- **All function signatures**: Include type hints
- **Return types**: Explicitly declared
- **Optional types**: Use `Optional[T]` or `T | None` for nullable values
- **Union types**: Used where multiple types are acceptable

### Import Organization

1. **Standard library**: First
2. **Third-party**: Second (FastAPI, SQLAlchemy, Pydantic)
3. **Local imports**: Last (`from app import ...`)

### Code Formatting

- **Black**: Code formatter (configured in `requirements.txt`)
- **Ruff**: Linter (configured in `requirements.txt`)
- **Consistent style**: Follows PEP 8 with project-specific adjustments

### Dependency Management

- **requirements.txt**: Pinned versions for reproducibility
- **Version pinning**: Specific versions (e.g., `fastapi==0.115.2`)
- **Security**: Regular updates for security patches

### Git Practices

- **Clear commit messages**: Descriptive of changes made
- **Feature branches**: Separate branches for features
- **Frequent commits**: Small, logical commits

---

## Summary

This codebase follows industry-standard practices for Python/FastAPI development:

-  **Layered architecture** with clear separation of concerns
-  **Type safety** through comprehensive type hints
-  **Validation** via Pydantic schemas
-  **Testing** with pytest and high coverage
-  **Documentation** with docstrings and comments
-  **Error handling** with appropriate HTTP status codes
-  **Security** through authentication and authorization
-  **Configuration** via environment variables
-  **Database** migrations with Alembic
-  **Code quality** tools (Black, Ruff, mypy)

These standards ensure maintainability, testability, and scalability of the codebase.

---

## Related Documentation

-  [Architecture Overview](./architecture.md) - System design and patterns
-  [Implementation Patterns](./implementation-patterns.md) - Code examples and patterns
-  [Documentation Index](./README.md) - Navigation guide

## Feedback

Found an issue or have a suggestion? Please open an issue or submit a pull request.