# Documentation

> **Welcome!** This directory contains comprehensive documentation for the Remote Servers Marketplace API project. All documentation is written in Markdown and optimized for readability, skimming, and AI/agent consumption.

## 📚 Documents

### [Coding Standards and Practices](./coding-standards.md)

**Comprehensive guide** covering coding conventions, architectural patterns, and best practices.

**Key topics:**

- ✅ Project architecture and code organization
- ✅ Naming conventions and code style
- ✅ API design patterns
- ✅ Database patterns and ORM usage
- ✅ Error handling strategies
- ✅ Authentication and authorization
- ✅ Testing practices
- ✅ Configuration management

**Use when:** Writing new code, reviewing PRs, onboarding developers, understanding conventions.

### [Architecture Overview](./architecture.md)

**High-level system architecture** documentation covering design decisions and system components.

**Key topics:**

- 🏗️ Technology stack
- 🏗️ Architecture patterns (layered, dependency injection, service layer)
- 🏗️ Data flow and request processing
- 🏗️ Database schema and relationships
- 🏗️ Security architecture
- 🏗️ Testing architecture
- 🏗️ Deployment considerations

**Use when:** Understanding system design, planning features, troubleshooting, making architectural decisions.

### [Implementation Patterns](./implementation-patterns.md)

**Copy-paste ready code examples** for common patterns used throughout the codebase.

**Key topics:**

- 💻 API endpoint structure
- 💻 Service layer functions
- 💻 CRUD operations
- 💻 Error handling patterns
- 💻 Authentication patterns
- 💻 State machine patterns
- 💻 Validation patterns

**Use when:** Implementing new features, learning patterns, troubleshooting common issues.

## 🚀 Quick Reference

### Code Organization

```
app/
├── api/          # HTTP endpoints (thin controllers)
├── services/     # Business logic (workflows, rules)
├── crud.py       # Database operations
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

## 📖 For AI Assistants

This documentation is optimized for AI consumption:

- All files are in Markdown format
- Code examples are copy-paste ready
- Clear structure with linkable headings

## 🤝 Contributing

When adding new features or making changes:

1. ✅ **Follow the coding standards** outlined in [`coding-standards.md`](./coding-standards.md)
2. ✅ **Maintain the architecture** patterns described in [`architecture.md`](./architecture.md)
3. ✅ **Update documentation** if you introduce new patterns or conventions
4. ✅ **Write tests** following the testing practices
5. ✅ **Update this README** if you add new documentation files

## ❓ Questions?

**Quick answers:**

- **Code style**: See [Coding Standards](./coding-standards.md)
- **System design**: See [Architecture Overview](./architecture.md)
- **Code examples**: See [Implementation Patterns](./implementation-patterns.md)
- **Specific implementation**: Check the codebase and inline documentation

## 🔗 Related Links

- [Main README](../README.md) - Project overview
- [Implementation Patterns](./implementation-patterns.md) - Code examples
- [Architecture Overview](./architecture.md) - System design
- [Coding Standards](./coding-standards.md) - Conventions and practices
