# Documentation

> **Welcome!** This directory contains comprehensive documentation for the Remote Servers Marketplace API project. All documentation is written in Markdown and optimized for readability, skimming, and AI/agent consumption.

##  Documents

### [Coding Standards and Practices](./coding-standards.md)

**Comprehensive guide** covering coding conventions, architectural patterns, and best practices.

**Key topics:**

-  Project architecture and code organization
-  Naming conventions and code style
-  API design patterns
-  Database patterns and ORM usage
-  Error handling strategies
-  Authentication and authorization
-  Testing practices
-  Configuration management

**Use when:** Writing new code, reviewing PRs, onboarding developers, understanding conventions.

### [Architecture Overview](./architecture.md)

**High-level system architecture** documentation covering design decisions and system components.

**Key topics:**

- ️ Technology stack
- ️ Architecture patterns (layered, dependency injection, service layer)
- ️ Data flow and request processing
- ️ Database schema and relationships
- ️ Security architecture
- ️ Testing architecture
- ️ Deployment considerations

**Use when:** Understanding system design, planning features, troubleshooting, making architectural decisions.

### [Implementation Patterns](./implementation-patterns.md)

**Copy-paste ready code examples** for common patterns used throughout the codebase.

**Key topics:**

-  API endpoint structure
-  Service layer functions
-  Repositoy layer operations
-  Error handling patterns
-  Authentication patterns
-  State machine patterns
-  Validation patterns

**Use when:** Implementing new features, learning patterns, troubleshooting common issues.

##  Quick Reference

### Code Organization

```
app/
├── api/          # HTTP endpoints (thin controllers)
├── repositories/ # Data access layer (queries and persistence logic).
├── services/     # Business logic (workflows, rules)
├── models.py     # SQLAlchemy ORM models
├── schemas.py    # Pydantic validation schemas
└── ...
```

### Naming Conventions

- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Database tables**: `plural_lowercase`

### Common Patterns

**API Endpoint:**

```python
@router.post("/", response_model=schemas.ResourceRead, status_code=201)
def create_resource(data: schemas.ResourceCreate, db: Session = Depends(get_db)):
    return crud.create_resource(db, data)
```

**Service Function:**

```python
def business_operation(db: Session, resource_id: int):
    resource = db.get(models.Resource, resource_id)
    if not resource:
        raise ValueError("Resource not found")
    # Business logic here
    db.commit()
    return resource
```

**CRUD Function:**

```python
def create_resource(db: Session, data: schemas.ResourceCreate):
    obj = models.Resource(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
```

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

##  For AI Assistants

This documentation is optimized for AI consumption:

- All files are in Markdown format
- Code examples are copy-paste ready
- Clear structure with linkable headings

##  Contributing

When adding new features or making changes:

1.  **Follow the coding standards** outlined in [`coding-standards.md`](./coding-standards.md)
2.  **Maintain the architecture** patterns described in [`architecture.md`](./architecture.md)
3.  **Update documentation** if you introduce new patterns or conventions
4.  **Write tests** following the testing practices
5.  **Update this README** if you add new documentation files

##  Questions?

**Quick answers:**

- **Code style**: See [Coding Standards](./coding-standards.md)
- **System design**: See [Architecture Overview](./architecture.md)
- **Code examples**: See [Implementation Patterns](./implementation-patterns.md)
- **Specific implementation**: Check the codebase and inline documentation

##  Related Links

- [Main README](../README.md) - Project overview
- [Implementation Patterns](./implementation-patterns.md) - Code examples
- [Architecture Overview](./architecture.md) - System design
- [Coding Standards](./coding-standards.md) - Conventions and practices