# Architecture Overview

> **Quick Start**: Understanding the system? Start here. Need code examples? See [Implementation Patterns](./implementation-patterns.md). Looking for standards? See [Coding Standards](./coding-standards.md).

This document provides a high-level overview of the Remote Servers Marketplace API architecture, design decisions, and system components.

## Quick Reference

| Component      | Technology       | Purpose                     |
| -------------- | ---------------- | --------------------------- |
| **Framework**  | FastAPI          | REST API framework          |
| **Database**   | PostgreSQL       | Data persistence            |
| **ORM**        | SQLAlchemy 2.0   | Database abstraction        |
| **Migrations** | Alembic          | Schema versioning           |
| **Validation** | Pydantic         | Request/response validation |
| **Auth**       | PyJWT + Supabase | Token-based authentication  |
| **Testing**    | pytest           | Test framework              |

## System Overview

The Remote Servers Marketplace is a RESTful API built with FastAPI that enables:

- **Providers** to list compute resources (servers) for rent
- **Buyers** to request bookings for specific time windows
- **Session management** for active server usage
- **Billing calculation** based on actual usage time

## Technology Stack

### Core Framework

- **FastAPI**: Modern, fast web framework for building APIs
- **Python 3.11+**: Programming language

### Database & ORM

- **PostgreSQL**: Relational database
- **SQLAlchemy 2.0**: ORM for database interactions
- **Alembic**: Database migration tool

### Validation & Serialization

- **Pydantic**: Data validation and settings management
- **Pydantic Settings**: Configuration management

### Authentication

- **PyJWT**: JWT token validation
- **Supabase**: JWT provider (production)
- **Mock tokens**: Development/testing support

### Testing

- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting
- **httpx**: HTTP client for testing

### Code Quality

- **Black**: Code formatter
- **Ruff**: Fast Python linter
- **mypy**: Static type checker

## Architecture Patterns

### 1. Layered Architecture

The application follows a strict layered architecture:

```
┌─────────────────────────────────────────┐
│         Presentation Layer               │
│  FastAPI Routes (app/api/*.py)         │
│  - HTTP request/response handling       │
│  - Authentication/authorization         │
│  - Input validation (Pydantic)          │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Application Layer                │
│  Business Logic (app/services/*.py)    │
│  - Workflow orchestration               │
│  - Business rules                       │
│  - State transitions                    │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Data Access Layer                │
│  CRUD Operations (app/crud.py)         │
│  - Database queries                     │
│  - Basic operations                     │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Domain Layer                    │
│  Models (app/models.py)                 │
│  - SQLAlchemy ORM models                │
│  - Relationships                        │
│  - Constraints                          │
└─────────────────────────────────────────┘
```

### 2. Dependency Injection

FastAPI's dependency injection system is used throughout:

- **Database sessions**: Injected via `get_db()` dependency
- **Authentication**: Injected via `get_current_identity()` dependency
- **Authorization**: Injected via `require_roles()` factory

**Benefits:**

- Testability: Easy to mock dependencies in tests
- Decoupling: Components don't create their own dependencies
- Lifecycle management: Automatic cleanup (e.g., DB session closing)

### 3. Service Layer Pattern

Business logic is separated into service modules:

**Why Services?**

- **Reusability**: Business logic can be called from multiple endpoints
- **Testability**: Services can be tested independently of HTTP layer
- **Complexity**: Handles multi-step workflows and validations

**Example Flow:**

```
API Endpoint → Service Function → CRUD Function → Database
```

### 4. Repository Pattern (Simplified)

CRUD operations are centralized in `crud.py`:

- **Separation**: Database queries separated from business logic
- **Consistency**: Standardized query patterns
- **Maintainability**: Database changes isolated to CRUD layer

## Data Flow

### Request Flow

```
1. HTTP Request
   ↓
2. FastAPI Router (app/api/*.py)
   - Validates authentication token
   - Checks authorization (roles)
   - Validates request body (Pydantic)
   ↓
3. Service Layer (app/services/*.py)
   - Applies business rules
   - Validates business constraints
   - Orchestrates workflow
   ↓
4. CRUD Layer (app/crud.py)
   - Builds database queries
   - Executes operations
   - Returns model instances
   ↓
5. Response Serialization
   - Pydantic schemas convert models to JSON
   - Returns HTTP response
```

### Booking Lifecycle Flow

```
REQUESTED → CONFIRMED → ACTIVE → COMPLETED
                ↓
            CANCELLED (can occur from REQUESTED or CONFIRMED)
```

**State Transitions:**

- **REQUESTED**: Initial state when buyer creates booking
- **CONFIRMED**: Provider approves the booking
- **ACTIVE**: Provider starts the session
- **COMPLETED**: Session ended, billing finalized
- **CANCELLED**: Booking cancelled before session starts

## Database Schema

### Entity Relationship Diagram

```
┌─────────────┐         ┌──────────────┐
│  Listings   │◄───┐    │   Bookings   │
│─────────────│    │    │──────────────│
│ id (PK)     │    │    │ id (PK)      │
│ title       │    └────│ listing_id   │
│ price       │         │ buyer_name   │
└─────────────┘         │ start_time   │
                        │ end_time     │
                        │ status       │
                        │ total_price_ │
                        │   estimate   │
                        │ active_      │
                        │   session_   │
                        │   start      │
                        │ active_      │
                        │   session_   │
                        │   end        │
                        │ actual_price_│
                        │   charged    │
                        │ usage_seconds│
└──────────────┘
```

### Key Relationships

- **One-to-Many**: One `Listing` can have many `Booking`s
- **Foreign Key**: `Booking.listing_id` → `Listing.id` (CASCADE delete)
- **Enum**: `Booking.status` uses `BookingStatus` enum

## Security Architecture

### Authentication Flow

```
1. Client sends request with Bearer token
   ↓
2. FastAPI extracts token from Authorization header
   ↓
3. get_current_identity() dependency:
   - Checks if Supabase JWT key configured
   - If yes: Validates JWT (RS256)
   - If no: Parses mock token (role:username)
   ↓
4. Returns identity dict: {role, username}
   ↓
5. require_roles() checks if role is allowed
   ↓
6. Request proceeds if authorized
```

### Authorization Model

**Role-Based Access Control (RBAC):**

| Role      | Permissions                                        |
| --------- | -------------------------------------------------- |
| buyer     | View listings, request bookings                    |
| provider  | Create listings, confirm bookings, manage sessions |
| admin     | Full access to all operations                      |
| org_admin | Organization-level admin (future use)              |

## Configuration Management

### Environment-Based Configuration

The application supports multiple environments:

- **local**: Development environment (uses `.env` file)
- **ci**: Continuous Integration (uses GitHub Secrets)
- **prod**: Production (uses environment variables)

### Configuration Sources (Priority Order)

1. **Environment variables** (highest priority)
2. **`.env` file** (local development)
3. **Default values** (fallback)

### Key Configuration Values

- `DATABASE_URL`: PostgreSQL connection string
- `SUPABASE_JWT_PUBLIC_KEY`: Public key for JWT validation
- `ENV`: Environment identifier
- `TEST_DATABASE_URL`: Separate DB for testing (optional)

## Testing Architecture

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_auth.py             # Authentication tests
├── test_bookings.py         # Booking CRUD tests
├── test_booking_lifecycle.py # Workflow tests
├── test_listings.py         # Listing tests
└── ...
```

### Test Isolation Strategy

1. **Session-scoped migrations**: Run once before all tests
2. **Transaction isolation**: Each test uses a transaction that rolls back
3. **Dependency override**: FastAPI dependencies replaced with test versions
4. **Mock authentication**: Mock tokens for testing (`Bearer role:username`)

### Test Types

- **Unit tests**: Test individual functions in isolation
- **Integration tests**: Test API endpoints with database
- **Workflow tests**: Test complete business workflows

## Deployment Architecture

### Containerization

- **Docker**: Application containerization
- **docker-compose.yml**: Local development environment
- **Dockerfile**: Production container definition

### Database Migrations

- **Alembic**: Handles schema versioning
- **Migration files**: Stored in `alembic/versions/`
- **Upgrade path**: Migrations applied automatically on deployment

## Scalability Considerations

### Current Design Supports

- **Horizontal scaling**: Stateless API design
- **Database connection pooling**: SQLAlchemy pool configuration
- **Caching**: Can be added at API layer (not currently implemented)
- **Load balancing**: Multiple API instances can share database

### Future Enhancements

- **Caching layer**: Redis for frequently accessed data
- **Message queue**: For async processing (e.g., email notifications)
- **API rate limiting**: Prevent abuse
- **Monitoring**: Application performance monitoring (APM)

## Error Handling Strategy

### Error Propagation

```
Database Error → CRUD Layer → Service Layer → API Layer → HTTP Response
```

### Error Types

1. **Validation Errors**: Handled by Pydantic (400 Bad Request)
2. **Business Logic Errors**: `ValueError` in services → 404/400 in API
3. **State Conflicts**: `HTTPException` with 409 Conflict
4. **Authentication Errors**: 401 Unauthorized
5. **Authorization Errors**: 403 Forbidden
6. **Not Found Errors**: 404 Not Found

## API Design Principles

### RESTful Design

- **Resource-based URLs**: `/api/v1/listings`, `/api/v1/bookings`
- **HTTP methods**: GET (read), POST (create), PUT (update)
- **Status codes**: Standard HTTP status codes
- **JSON**: Request and response bodies in JSON

### API Versioning

- **URL versioning**: `/api/v1/` prefix
- **Future-proofing**: Allows breaking changes in v2 without affecting v1

### Response Consistency

- **Structured responses**: Always JSON
- **Error format**: `{"detail": "error message"}`
- **Success format**: Resource objects or arrays

## Performance Considerations

### Database Optimization

- **Indexes**: Primary keys automatically indexed
- **Connection pooling**: SQLAlchemy pool configuration
- **Query optimization**: Eager loading where appropriate

### API Performance

- **Async support**: FastAPI supports async endpoints (not currently used)
- **Response serialization**: Efficient Pydantic serialization
- **Minimal data transfer**: Only required fields in responses

## Monitoring and Observability

### Current State

- **Health endpoint**: `/api/v1/health` for uptime monitoring
- **Error logging**: Standard Python logging (can be enhanced)

### Recommended Enhancements

- **Structured logging**: JSON logs for better parsing
- **Metrics**: Request counts, response times, error rates
- **Tracing**: Distributed tracing for request flows
- **Alerts**: Automated alerts for errors and performance issues

## Conclusion

This architecture provides:

✅ **Separation of concerns** through layered design
✅ **Testability** through dependency injection
✅ **Scalability** through stateless design
✅ **Maintainability** through clear structure
✅ **Security** through authentication and authorization
✅ **Flexibility** through configuration management

The design follows industry best practices and can evolve to meet future requirements.

---

## Related Documentation

- 📖 [Coding Standards](./coding-standards.md) - Code conventions and practices
- 📖 [Implementation Patterns](./implementation-patterns.md) - Code examples and patterns
- 📖 [Documentation Index](./README.md) - Navigation guide
