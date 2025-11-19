# Coding Standards and Practices

> **Quick Start**: New to the codebase? Start with [Code Organization](#code-organization) and [Naming Conventions](#naming-conventions). Need examples? See [Implementation Patterns](./implementation-patterns.md).

This document outlines the coding standards, architectural patterns, and best practices followed during the implementation of the Remote Servers Marketplace API.

## Quick Reference

| Topic                 | Key Rule                                          | See Section                                                      |
| --------------------- | ------------------------------------------------- | ---------------------------------------------------------------- |
| **File naming**       | `snake_case.py`                                   | [Naming Conventions](#naming-conventions)                        |
| **Class naming**      | `PascalCase`                                      | [Naming Conventions](#naming-conventions)                        |
| **Function naming**   | `snake_case()`                                    | [Naming Conventions](#naming-conventions)                        |
| **API endpoints**     | Thin controllers → Services → CRUD                | [API Design Patterns](#api-design-patterns)                      |
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

The project follows a **layered architecture** pattern with clear separation of concerns:

```
┌─────────────────────────────────────┐
│         API Layer (FastAPI)         │  ← HTTP endpoints, request/response handling
│    app/api/listings.py              │
│    app/api/bookings.py              │
├─────────────────────────────────────┤
│      Service Layer (Business Logic)  │  ← Business rules, workflow orchestration
│    app/services/bookings_service.py │
├─────────────────────────────────────┤
│         CRUD Layer                  │  ← Database operations, data access
│    app/crud.py                      │
├─────────────────────────────────────┤
│         Models Layer                │  ← SQLAlchemy ORM models
│    app/models.py                    │
├─────────────────────────────────────┤
│         Schemas Layer               │  ← Pydantic validation schemas
│    app/schemas.py                   │
└─────────────────────────────────────┘
```

### Key Principles

- ✅ **Separation of Concerns**: Each layer has a distinct responsibility
- ✅ **Dependency Injection**: FastAPI's dependency system used throughout
- ✅ **Single Responsibility**: Each module/function has one clear purpose
- ✅ **DRY (Don't Repeat Yourself)**: Shared logic extracted to reusable functions

> 💡 **Tip**: When adding a new feature, ask: "Which layer does this belong to?" Keep API routes thin, business logic in services, and database operations in CRUD.

---

## Code Organization

### Directory Structure

```
app/
├── __init__.py              # Package initialization
├── main.py                  # FastAPI app entry point
├── config.py                # Configuration management
├── database.py              # Database connection & session management
├── models.py                # SQLAlchemy ORM models
├── schemas.py               # Pydantic validation schemas
├── crud.py                  # Basic CRUD operations
├── auth.py                  # Authentication & authorization logic
├── seed.py                  # Database seeding utilities
├── api/                     # API endpoint modules
│   ├── __init__.py
│   ├── listings.py          # Listing endpoints
│   └── bookings.py          # Booking endpoints
└── services/                # Business logic services
    ├── __init__.py
    └── bookings_service.py  # Booking workflow logic
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

3. **CRUD** (`app/crud.py`): Simple database operations

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

- ✅ **Snake_case** for all Python files: `bookings_service.py`, `test_auth.py`
- ✅ **Descriptive names**: Files should clearly indicate their purpose
- ✅ **Plural for collections**: `listings.py`, `bookings.py` (API routes)

**Examples:**

```python
# ✅ Good
bookings_service.py
test_booking_lifecycle.py

# ❌ Bad
service.py
test1.py
```

### Classes

- ✅ **PascalCase**: `Listing`, `Booking`, `BookingStatus`, `Settings`
- ✅ **Descriptive nouns**: Classes represent entities or concepts
- ✅ **Suffix conventions**:
  - **Models**: `Listing`, `Booking` (no suffix)
  - **Schemas**: `ListingCreate`, `ListingRead`, `BookingCreate` (action suffix)
  - **Enums**: `BookingStatus` (descriptive name)

**Examples:**

```python
# ✅ Good
class Listing(Base): ...
class ListingCreate(BaseModel): ...
class BookingStatus(str, Enum): ...

# ❌ Bad
class listing(Base): ...
class CreateListing(BaseModel): ...
```

### Functions and Variables

- ✅ **snake_case**: `create_booking()`, `get_listings()`, `buyer_name`
- ✅ **Verbs for functions**: `create_`, `get_`, `list_`, `update_`, `delete_`
- ✅ **Nouns for variables**: `booking_id`, `listing`, `db_session`

**Examples:**

```python
# ✅ Good
def create_booking(...): ...
def get_listings(...): ...
booking_id = 123

# ❌ Bad
def CreateBooking(...): ...
def getListings(...): ...
bookingId = 123
```

### Constants

- **UPPER_SNAKE_CASE**: `DATABASE_URL`, `SUPABASE_JWT_PUBLIC_KEY`
- Used for configuration values and environment variables

### Database Tables

- **Plural, lowercase**: `listings`, `bookings`
- **Snake_case** for column names: `buyer_name`, `start_time`, `active_session_start`

---

## API Design Patterns

### RESTful Endpoints

The API follows REST principles:

- **Resource-based URLs**: `/api/v1/listings`, `/api/v1/bookings`
- **HTTP methods**: GET (read), POST (create), PUT (update), DELETE (remove)
- **Status codes**: 200 (success), 201 (created), 400 (bad request), 404 (not found), 409 (conflict)

### Endpoint Structure

```python
@router.post(
    "/",
    response_model=schemas.ListingRead,
    status_code=201,
    dependencies=[Depends(require_roles("provider", "admin"))],
)
def create_listing(listing: schemas.ListingCreate, db: Session = Depends(get_db)):
    """
    Create a new listing (only allowed for providers or admins).
    Listings represent available resources or servers that buyers can book.
    """
    return crud.create_listing(db, listing)
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
    """Schema for creating a new listing."""
    title: str = Field(min_length=1)
    price: float = Field(ge=0)

class ListingRead(ListingCreate):
    """Schema for reading listing data from DB."""
    id: int
    model_config = ConfigDict(from_attributes=True)
```

---

## Database Patterns

### SQLAlchemy ORM Usage

**Model Definition Pattern:**

```python
class Listing(Base):
    """Represents a rentable compute resource or server."""
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    price = Column(Float, nullable=False)

    # Relationships
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
    FastAPI dependency for providing a scoped database session.
    Ensures session is closed after request completes.
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

> 💡 **Common mistake**: Don't raise `HTTPException` in CRUD functions. Use `ValueError` and let the API layer handle HTTP concerns.

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
def get_current_identity(
    creds: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Main dependency used by all protected endpoints.
    Automatically selects between:
    - Real JWT validation (if Supabase key set)
    - Mock parsing for local/testing environments
    """
    if not creds:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = creds.credentials
    if settings.SUPABASE_JWT_PUBLIC_KEY:
        return _decode_jwt_token(token)
    return _parse_mock_token(token)
```

### Role-Based Access Control

**Factory Pattern for Role Requirements:**

```python
def require_roles(*allowed_roles):
    """
    Factory dependency generator.
    Restricts endpoint access to users whose 'role' is in allowed_roles.
    """
    def dependency(identity=Depends(get_current_identity)):
        if identity["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return identity
    return dependency
```

**Usage:**

```python
@router.post(
    "/",
    dependencies=[Depends(require_roles("provider", "admin"))],
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
├── conftest.py              # Shared fixtures and test configuration
├── test_auth.py             # Authentication tests
├── test_bookings.py         # Booking CRUD tests
├── test_booking_lifecycle.py # Workflow tests
├── test_listings.py         # Listing tests
└── ...
```

### Test Fixtures

**Database Setup:**

```python
@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    """Apply Alembic migrations once before tests."""
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    command.upgrade(alembic_cfg, "head")
    yield

@pytest.fixture()
def db_session():
    """Create a transactional session for each test (isolated)."""
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

**Integration Tests:**

```python
@pytest.mark.integration
def test_create_and_read_booking(client):
    ...
```

**Markers defined in `pytest.ini`:**

- `integration`: Marks tests that require database/external services

### Test Coverage

- **Coverage reporting**: Configured via `pytest-cov`
- **Coverage targets**: Aim for high coverage of business logic
- **Exclusions**: `app/seed.py` excluded from coverage (utility script)

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
    """
    Centralized configuration class.
    Automatically loads values from environment variables
    (including GitHub Secrets during CI/CD runs).
    """
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

    ENV: str = Field(default="local")
    DATABASE_URL: str | None = os.getenv("DATABASE_URL")
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
This service layer file handles all business logic related to Bookings.
Each function corresponds to an action in the booking lifecycle:
request → confirm → cancel → start → end
"""
```

**Function Docstrings:**

```python
def request_booking(db: Session, listing_id: int, buyer_name: str, start_time: datetime, end_time: datetime):
    """
    Create a new booking request for a specific listing.

    Steps:
    1. Fetch the listing from the database using its ID.
    2. Validate that the listing exists.
    3. Calculate the estimated total price based on duration (in hours * price).
    4. Create a new Booking record with 'REQUESTED' status.
    5. Persist and return the new booking.
    """
```

**Class Docstrings:**

```python
class Listing(Base):
    """Represents a rentable compute resource or server."""
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

- ✅ **Layered architecture** with clear separation of concerns
- ✅ **Type safety** through comprehensive type hints
- ✅ **Validation** via Pydantic schemas
- ✅ **Testing** with pytest and high coverage
- ✅ **Documentation** with docstrings and comments
- ✅ **Error handling** with appropriate HTTP status codes
- ✅ **Security** through authentication and authorization
- ✅ **Configuration** via environment variables
- ✅ **Database** migrations with Alembic
- ✅ **Code quality** tools (Black, Ruff, mypy)

These standards ensure maintainability, testability, and scalability of the codebase.

---

## Related Documentation

- 📖 [Architecture Overview](./architecture.md) - System design and patterns
- 📖 [Implementation Patterns](./implementation-patterns.md) - Code examples and patterns
- 📖 [Documentation Index](./README.md) - Navigation guide

## Feedback

Found an issue or have a suggestion? Please open an issue or submit a pull request.
