# Implementation Patterns

> **Quick Start**: Copy-paste ready code examples for common patterns. Need context? See [Architecture Overview](./architecture.md) and [Coding Standards](./coding-standards.md).

This document describes common implementation patterns used throughout the codebase, with code examples and best practices.

## Quick Reference

| Pattern            | When to Use                   | Example                                           |
| ------------------ | ----------------------------- | ------------------------------------------------- |
| **API Endpoint**   | Creating HTTP endpoints       | [API Endpoint Pattern](#api-endpoint-pattern)     |
| **Service Layer**  | Business logic & workflows    | [Service Layer Pattern](#service-layer-pattern)   |
| **CRUD**           | Simple database operations    | [CRUD Pattern](#crud-pattern)                     |
| **Error Handling** | Handling errors across layers | [Error Handling Pattern](#error-handling-pattern) |
| **Authentication** | Protecting endpoints          | [Authentication Pattern](#authentication-pattern) |
| **State Machine**  | Managing status transitions   | [State Machine Pattern](#state-machine-pattern)   |

## Table of Contents

1. [API Endpoint Pattern](#api-endpoint-pattern)
2. [Service Layer Pattern](#service-layer-pattern)
3. [CRUD Pattern](#crud-pattern)
4. [Error Handling Pattern](#error-handling-pattern)
5. [Authentication Pattern](#authentication-pattern)
6. [Database Session Pattern](#database-session-pattern)
7. [State Machine Pattern](#state-machine-pattern)
8. [Validation Pattern](#validation-pattern)

---

## API Endpoint Pattern

### Standard Endpoint Structure

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db
from app.auth import require_roles

router = APIRouter()

@router.post(
    "/",
    response_model=schemas.ResourceRead,
    status_code=201,
    dependencies=[Depends(require_roles("provider", "admin"))],
)
def create_resource(
    payload: schemas.ResourceCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new resource.

    Clear description of what this endpoint does, who can use it,
    and any important behavior or constraints.
    """
    try:
        return crud.create_resource(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

### Pattern Elements

1. **Router**: Use `APIRouter()` for modular endpoints
2. **Decorator**: Route decorator with method, path, response model, status code
3. **Dependencies**: Authentication/authorization via `Depends()`
4. **Type Hints**: All parameters explicitly typed
5. **Docstring**: Clear description of endpoint purpose
6. **Error Handling**: Convert service errors to HTTP exceptions
7. **Return**: Return model instances (serialized via response_model)

### Endpoint Types

**CRUD Endpoints:**

```python
@router.post("/", response_model=schemas.ResourceRead, status_code=201)
def create_resource(...): ...

@router.get("/", response_model=list[schemas.ResourceRead])
def list_resources(...): ...

@router.get("/{resource_id}", response_model=schemas.ResourceRead)
def get_resource(...): ...

@router.put("/{resource_id}", response_model=schemas.ResourceRead)
def update_resource(...): ...

@router.delete("/{resource_id}", status_code=204)
def delete_resource(...): ...
```

**Action Endpoints:**

```python
@router.put("/{booking_id}/confirm", response_model=schemas.BookingRead)
def confirm_booking(booking_id: int, db: Session = Depends(get_db)):
    """Provider confirms a pending booking."""
    try:
        return bookings_service.confirm_booking(db, booking_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

---

## Service Layer Pattern

### Purpose

Services contain business logic that:

- Orchestrates multiple operations
- Enforces business rules
- Manages state transitions
- Validates complex constraints

### Standard Service Function

```python
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app import models

def perform_business_operation(
    db: Session,
    resource_id: int,
    additional_param: str
):
    """
    Perform a business operation with clear steps.

    Steps:
    1. Fetch and validate resource exists
    2. Validate business constraints
    3. Perform operation
    4. Update state
    5. Persist changes
    6. Return updated resource
    """
    # Step 1: Fetch resource
    resource = db.get(models.Resource, resource_id)
    if not resource:
        raise ValueError("Resource not found")

    # Step 2: Validate business constraints
    if resource.status != models.ResourceStatus.ALLOWED_STATE:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot perform operation; current status is '{resource.status}'"
        )

    # Step 3: Perform operation
    resource.status = models.ResourceStatus.NEW_STATE
    resource.updated_at = datetime.now(timezone.utc)

    # Step 4: Persist
    db.commit()
    db.refresh(resource)

    # Step 5: Return
    return resource
```

### Error Handling in Services

**Business Logic Errors:**

```python
# Use ValueError for business logic errors (caught by API layer)
if not listing:
    raise ValueError("Listing not found")
```

**HTTP-Specific Errors:**

```python
# Use HTTPException for HTTP-specific errors (bubbles up unchanged)
if booking.status != models.BookingStatus.CONFIRMED:
    raise HTTPException(
        status_code=409,
        detail=f"Cannot start; current status is '{booking.status}'"
    )
```

---

## CRUD Pattern

### Create Operation

```python
def create_resource(db: Session, data: schemas.ResourceCreate):
    """
    Create a new resource record and persist to the database.
    """
    obj = models.Resource(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
```

**Pattern:**

1. Create model instance from schema data
2. Add to session
3. Commit transaction
4. Refresh to get DB-generated fields (e.g., id)
5. Return instance

### Read Operations

```python
def get_resource(db: Session, resource_id: int):
    """Get a single resource by ID."""
    return db.get(models.Resource, resource_id)

def list_resources(db: Session):
    """Return all resources sorted by ID (ascending)."""
    return db.query(models.Resource).order_by(models.Resource.id.asc()).all()
```

**Pattern:**

- Use `db.get()` for single record by primary key
- Use `db.query()` for filtered/sorted queries
- Always specify sort order for list operations

### Update Operation

```python
def update_resource(db: Session, resource_id: int, data: schemas.ResourceUpdate):
    """Update an existing resource."""
    resource = db.get(models.Resource, resource_id)
    if not resource:
        raise ValueError("Resource not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(resource, key, value)

    db.commit()
    db.refresh(resource)
    return resource
```

**Pattern:**

- Fetch existing record
- Update fields from schema (exclude_unset=True for partial updates)
- Commit and refresh
- Return updated instance

### Delete Operation

```python
def delete_resource(db: Session, resource_id: int):
    """Delete a resource by ID."""
    resource = db.get(models.Resource, resource_id)
    if not resource:
        raise ValueError("Resource not found")

    db.delete(resource)
    db.commit()
    return resource
```

---

## Error Handling Pattern

### Three-Layer Error Handling

**1. Service Layer (Business Logic):**

```python
# Raises ValueError for business logic errors
if not listing:
    raise ValueError("Listing not found")
```

**2. Service Layer (HTTP-Specific):**

```python
# Raises HTTPException for HTTP-specific errors
if booking.status != models.BookingStatus.CONFIRMED:
    raise HTTPException(status_code=409, detail="Cannot start; booking not confirmed")
```

**3. API Layer:**

```python
# Catches ValueError and converts to HTTPException
try:
    return bookings_service.request_booking(...)
except ValueError as e:
    raise HTTPException(status_code=404, detail=str(e))
except HTTPException:
    # Allow HTTPExceptions to bubble up unchanged
    raise
except Exception as e:
    # Unexpected errors
    raise HTTPException(status_code=400, detail=str(e))
```

### Status Code Mapping

| Error Type     | Service Layer                      | API Layer            | HTTP Status |
| -------------- | ---------------------------------- | -------------------- | ----------- |
| Not found      | `ValueError("Resource not found")` | `HTTPException(404)` | 404         |
| Invalid input  | `ValueError("Invalid data")`       | `HTTPException(400)` | 400         |
| State conflict | `HTTPException(409)`               | Pass through         | 409         |
| Auth required  | N/A                                | `HTTPException(401)` | 401         |
| Forbidden      | N/A                                | `HTTPException(403)` | 403         |

---

## Authentication Pattern

### Protected Endpoint

```python
from app.auth import require_roles

@router.post(
    "/",
    dependencies=[Depends(require_roles("provider", "admin"))],
)
def create_listing(...):
    """Only providers and admins can create listings."""
    ...
```

### Multiple Role Access

```python
# Allow multiple roles
dependencies=[Depends(require_roles("provider", "admin"))]

# Single role
dependencies=[Depends(require_roles("admin"))]

# Public endpoint (no dependency)
# No dependencies parameter needed
```

### Getting Current User (if needed)

```python
from app.auth import get_current_identity

@router.get("/me")
def get_current_user(identity=Depends(get_current_identity)):
    """Get current authenticated user information."""
    return {
        "role": identity["role"],
        "username": identity["username"]
    }
```

---

## Database Session Pattern

### Dependency Injection

```python
from app.database import get_db

@router.get("/")
def list_resources(db: Session = Depends(get_db)):
    """Get all resources."""
    return crud.list_resources(db)
```

### Session Lifecycle

1. **Request starts**: FastAPI calls `get_db()` dependency
2. **Session created**: New database session created
3. **Request processing**: Session used throughout request
4. **Request ends**: Session automatically closed (via `finally` block)

### Transaction Management

```python
# Automatic transaction (default)
def create_resource(db: Session, data: schemas.ResourceCreate):
    obj = models.Resource(**data.model_dump())
    db.add(obj)
    db.commit()  # Explicit commit required
    return obj

# Rollback on error (automatic)
# If exception occurs before commit, transaction rolls back
```

---

## State Machine Pattern

### Booking Status State Machine

```python
class BookingStatus(str, Enum):
    REQUESTED = "requested"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# State transitions:
# REQUESTED → CONFIRMED → ACTIVE → COMPLETED
# REQUESTED → CANCELLED
# CONFIRMED → CANCELLED
```

### State Transition Validation

```python
def start_session(db: Session, booking_id: int):
    """Start session - only from CONFIRMED state."""
    booking = db.get(models.Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Validate current state
    if booking.status != models.BookingStatus.CONFIRMED:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot start; current status is '{booking.status}'"
        )

    # Transition state
    booking.status = models.BookingStatus.ACTIVE
    booking.active_session_start = datetime.now(timezone.utc)

    db.commit()
    return booking
```

### State Transition Rules

- **Validate source state**: Check current state before transition
- **Validate conditions**: Check business rules (timing, relationships)
- **Update state**: Set new status
- **Update related fields**: Update timestamps, flags, etc.
- **Persist**: Commit changes

---

## Validation Pattern

### Schema Validation (Pydantic)

```python
from pydantic import BaseModel, Field

class ListingCreate(BaseModel):
    """Schema for creating a new listing."""
    title: str = Field(min_length=1, description="Listing title")
    price: float = Field(ge=0, description="Price per hour")

class ListingRead(ListingCreate):
    """Schema for reading listing data."""
    id: int
    model_config = ConfigDict(from_attributes=True)
```

### Field Validation Rules

```python
# String validation
title: str = Field(min_length=1, max_length=100)

# Number validation
price: float = Field(ge=0, le=10000)  # >= 0, <= 10000

# Optional fields
description: Optional[str] = None

# Default values
status: BookingStatus = BookingStatus.REQUESTED
```

### Business Logic Validation

```python
def create_booking(db: Session, data: schemas.BookingCreate):
    """Create booking with business rule validation."""
    # Schema validation happens automatically (Pydantic)
    # Additional business validation:

    if data.end_time <= data.start_time:
        raise HTTPException(
            status_code=400,
            detail="end_time must be after start_time"
        )

    listing = db.get(models.Listing, data.listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    # Proceed with creation
    ...
```

### Validation Layers

1. **Pydantic**: Schema-level validation (types, constraints)
2. **Service Layer**: Business rule validation (relationships, state)
3. **Database**: Constraint validation (foreign keys, unique constraints)

---

## Common Patterns Summary

### Pattern Checklist

When implementing a new feature:

- [ ] **API Endpoint**: Follow standard endpoint structure
- [ ] **Service Function**: Extract business logic to service layer
- [ ] **CRUD Function**: Use CRUD pattern for database operations
- [ ] **Error Handling**: Use appropriate error types and status codes
- [ ] **Authentication**: Add role-based access control if needed
- [ ] **Validation**: Use Pydantic schemas and business rule validation
- [ ] **Type Hints**: Add type hints to all functions
- [ ] **Docstrings**: Document purpose, parameters, and behavior
- [ ] **Tests**: Write tests following testing patterns

### Code Review Checklist

When reviewing code:

- [ ] Follows naming conventions
- [ ] Uses appropriate layer (API/Service/CRUD)
- [ ] Error handling is consistent
- [ ] Type hints are present
- [ ] Docstrings are clear
- [ ] Authentication/authorization is correct
- [ ] Database operations use proper patterns
- [ ] State transitions are validated

---

These patterns ensure consistency, maintainability, and testability across the codebase.

---

## Related Documentation

- 📖 [Coding Standards](./coding-standards.md) - Code conventions and practices
- 📖 [Architecture Overview](./architecture.md) - System design and patterns
- 📖 [Documentation Index](./README.md) - Navigation guide

## Troubleshooting

### Common Issues

**Q: Where should I put business logic?**
A: Use the service layer (`app/services/`) for business logic. Keep API endpoints thin.

**Q: How do I handle errors?**
A: Raise `ValueError` in services, catch and convert to `HTTPException` in API layer.

**Q: How do I test protected endpoints?**
A: Use mock tokens: `headers = {"Authorization": "Bearer provider:alice"}`

**Q: How do I add a new endpoint?**
A: Follow the [API Endpoint Pattern](#api-endpoint-pattern) - create route, add service function if needed, add CRUD if needed.
