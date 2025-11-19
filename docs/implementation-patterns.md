# Implementation Patterns

> **Quick Start**: Copy-paste ready code examples for common patterns. Need context? See [Architecture Overview](./architecture.md) and [Coding Standards](./coding-standards.md).

This document describes common implementation patterns used throughout the codebase, with code examples and best practices.

## Quick Reference

| Pattern            | When to Use                   | Example                                           |
| ------------------ | ----------------------------- | ------------------------------------------------- |
| **API Endpoint**   | Creating HTTP endpoints       | [API Endpoint Pattern](#api-endpoint-pattern)     |
| **Service Layer**  | Business logic & workflows    | [Service Layer Pattern](#service-layer-pattern)   |
| **Repository**     | Simple database operations    | [Repository Layer Pattern](#repo-layer-pattern)   |
| **Error Handling** | Handling errors across layers | [Error Handling Pattern](#error-handling-pattern) |
| **Authentication** | Protecting endpoints          | [Authentication Pattern](#authentication-pattern) |
| **State Machine**  | Managing status transitions   | [State Machine Pattern](#state-machine-pattern)   |

## Table of Contents

1. [API Endpoint Pattern](#api-endpoint-pattern)
2. [Service Layer Pattern](#service-layer-pattern)
3. [Repository Layer Pattern](#repo-layer-pattern)
4. [Error Handling Pattern](#error-handling-pattern)
5. [Authentication Pattern](#authentication-pattern)
6. [Database Session Pattern](#database-session-pattern)
7. [State Machine Pattern](#state-machine-pattern)
8. [Validation Pattern](#validation-pattern)

---

## API Endpoint Pattern

### Pattern Elements

1. **Router**: Use `APIRouter()` for modular endpoints
2. **Decorator**: Route decorator with method, path, response model, status code
3. **Dependencies**: Authentication/authorization via `Depends()`
4. **Type Hints**: All parameters explicitly typed
5. **Docstring**: Clear description of endpoint purpose
6. **Error Handling**: Convert service errors to HTTP exceptions
7. **Return**: Return model instances (serialized via response_model)

### Endpoint Types

**Action Endpoints:**

```python
@router.put("/{booking_id}/confirm", response_model=schemas.BookingRead)
def confirm_booking(booking_id: int, db: Session = Depends(get_db)):
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
    raise HTTPException(status_code=409, detail=f"Cannot start; current status is '{booking.status}'")
```

---

## Repository Layer Pattern

### Create Operation

```python
def create_listing(db: Session, data: schemas.ListingCreate):
    """Create a new listing record and persist to the database."""
    obj = models.Listing(**data.model_dump()) #Pydantic model_dump() gives us regular dict data ready to pass to SQLAlchemy
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
def get_listing_by_id(db: Session, listing_id: int) -> models.Listing | None:
    """Fetch a listing by its primary key so search results are deterministic."""
    return db.get(models.Listing, listing_id)

def get_listings(db: Session):
    """Return all listings sorted by ID."""
    return db.query(models.Listing).order_by(models.Listing.id.asc()).all()
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
#Validate session timing window
if now < booking.start_time:
    raise HTTPException(status_code=400, detail="Cannot start before booking start_time")
if now > booking.end_time:
    raise HTTPException(status_code=400, detail="Cannot start; booking window expired")
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
@router.post(
    "/",
    response_model=schemas.ListingRead,
    status_code=201,
    dependencies=[Depends(require_roles(models.UserRole.PROVIDER, models.UserRole.ADMIN))],
)
def create_listing(listing: schemas.ListingCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    ...
```

### Multiple Role Access

```python
# Allow multiple roles
dependencies=[Depends(require_roles(models.UserRole.PROVIDER, models.UserRole.ADMIN))]

# Single role
dependencies=[Depends(require_roles(models.UserRole.ADMIN))]

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
from app.repositories import listing_repository

def list_listings(db: Session):
    """
    The repository only does low-level DB writes.
    This service layer is where we enforce business rules.
    """
    return listing_repository.get_listings(db)
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
    """
    A session can only begin during the reserved window.
    We disallow starting outside it because usage is tied to billing
    and the hosting provider's capacity planning.
    """
    booking = booking_repository.get_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.status != models.BookingStatus.CONFIRMED:
        raise HTTPException(status_code=409, detail=f"Cannot start; current status is '{booking.status}'")

    if booking.active_session_start is not None:
        raise HTTPException(status_code=409, detail="Session already started")

    now = datetime.now(timezone.utc)

    if now < booking.start_time:
        raise HTTPException(status_code=400, detail="Cannot start before booking start_time")
    if now > booking.end_time:
        raise HTTPException(status_code=400, detail="Cannot start; booking window expired")

    booking.active_session_start = now
    booking.status = models.BookingStatus.ACTIVE

    db.commit()
    db.refresh(booking)
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
    """Payload sent by providers or admins when creating a new listing."""
    machine_id: int
    title: str = Field(min_length=1)
    price: float = Field(ge=0)

class ListingRead(ListingCreate):
    id: int
    machine: Optional[MachineRead] = None
    model_config = ConfigDict(from_attributes=True)
```

### Field Validation Rules

```python
# String validation
title: str = Field(min_length=1)

# Number validation
price: float = Field(ge=0)

# Optional fields
description: Optional[str] = None

# Default values
status: BookingStatus = BookingStatus.REQUESTED
```

### Business Logic Validation

```python
def create_booking(db: Session, data: schemas.BookingCreate) -> models.Booking:
    """
    This is the low-level primitive used by the service layer to create a booking.
    It assumes the caller manages the booking process (separation of concerns),
    and it performs curcial validation:
    1. A listing must exist
    2. The time window must be valid
    3. Necessitates a buyer id
    It also computes the estimated price based on whole hours.
    """
    listing = db.get(models.Listing, data.listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    if data.end_time <= data.start_time:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")

    if data.buyer_user_id is None:
        raise HTTPException(
            status_code=400,
            detail="buyer_user_id is required for admin booking creation",
        )
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
- [ ] **Repository Function**: Use repository layer pattern for database operations
- [ ] **Error Handling**: Use appropriate error types and status codes
- [ ] **Authentication**: Add role-based access control if needed
- [ ] **Validation**: Use Pydantic schemas and business rule validation
- [ ] **Type Hints**: Add type hints to all functions
- [ ] **Docstrings**: Document purpose, parameters, and behavior
- [ ] **Tests**: Write tests following testing patterns

### Code Review Checklist

When reviewing code:

- [ ] Follows naming conventions
- [ ] Uses appropriate layer (API/Service/Repository)
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

-  [Coding Standards](./coding-standards.md) - Code conventions and practices
-  [Architecture Overview](./architecture.md) - System design and patterns
-  [Documentation Index](./README.md) - Navigation guide

## Troubleshooting

### Common Issues

**Q: Where should I put business logic?**
A: Use the service layer (`app/services/`) for business logic. Keep API endpoints thin.

**Q: How do I handle errors?**
A: Raise `ValueError` in services, catch and convert to `HTTPException` in API layer.

**Q: How do I test protected endpoints?**
A: Use mock tokens: `headers = {"Authorization": "Bearer provider:alice"}`

**Q: How do I add a new endpoint?**
A: Follow the [API Endpoint Pattern](#api-endpoint-pattern) - create route, add service function if needed, add the repository if needed.