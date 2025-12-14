# SuperVision Remote Servers Marketplace - Part 4

A full-stack platform for renting high-performance computing (HPC) and AI/ML servers.  
Providers can list dedicated machines, and buyers can securely book compute resources.  
Built with FastAPI, PostgreSQL, Supabase Auth, Tailwind/Flowbite, pytest, GitHub Actions CI/CD, and deployed on Render.

---

## Live site:
https://remote-servers-marketplace-test.onrender.com/

---

## Overview

The SuperVision Remote Servers marketplace is a fully functional HPC server-rental platform that implements comprehensive testing, deployment, and maintenance practices. This Part 4 submission demonstrates:

- **Testing Excellence**: Unit, integration, and user acceptance testing with ≥80% coverage
- **Production Deployment**: Fully deployed cloud application on Render Web Services
- **Maintenance Planning**: Comprehensive monitoring, updates, and enhancement roadmap
- **Collaborative Development**: Well-documented Git workflows and team collaboration

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
- GitHub Actions CI/CD
- Render Web Services deployment
- Coverage reports and artifact uploads
- Automated testing pipeline

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
- Submit compliance wipe attestations

### Buyer Features
- Browse all server listings with real-time metrics
- Request and manage bookings
- View current and past bookings
- Cancel pending bookings
- Access machine credentials for active sessions

### Administrative Features
- Full booking lifecycle management
- Dispute resolution system
- Organization and user management
- Invoice generation and management
- Compliance verification

### General Features
- Fully responsive UI (Tailwind/Flowbite)
- Dynamic role-based template rendering
- Health endpoint `/api/v1/health`
- Inline API documentation via FastAPI docs:  
  https://remote-servers-marketplace-test.onrender.com/docs
- Comprehensive error handling and validation

---

## Project Structure

The application follows domain-driven design principles with 15+ independent domains:
```
app/
├── auth/ # Authentication and authorization
├── bookings/ # Booking lifecycle management
├── payments/ # Payment processing and Stripe integration
├── listings/ # Server listings with search and filtering
├── machines/ # Machine registration and management
├── compliance/ # Wipe attestation and regulatory compliance
├── organizations/ # Organization and team management
├── invoices/ # Billing and invoice generation
├── disputes/ # Dispute resolution system
├── credentials/ # Access credential issuance and revocation
├── benchmarks/ # Performance benchmarking
├── metrics/ # Machine performance monitoring
├── providers/ # Provider profiles and verification
├── notifications/ # Email notifications and alerts
└── users/ # User management
```

Each domain contains: models, schemas, repository, service, public API, routes, and tests.

---

## Testing Implementation

### Test Coverage and Quality
- **Coverage Requirement**: ≥80% line coverage enforced by CI pipeline
- **Test Types**: Unit tests, integration tests, domain tests
- **Test Domains**: All 15+ application domains thoroughly tested
- **CI Integration**: Automated testing on every push and pull request

### Testing Strategy
- **Domain Isolation**: Each domain has independent test suites
- **Mock External Services**: Stripe, Supabase, and email services mocked for reliable testing
- **Database Transactions**: Tests run in isolated transactions with automatic rollback
- **Factory Patterns**: Test data factories for consistent test data generation

### User Acceptance Testing (UAT)
- **Stakeholder Involvement**: Direct testing by stakeholders with real-world scenarios
- **Documentation**: UAT reports documenting feature validation and user experience
- **Feedback Integration**: Stakeholder feedback incorporated into development cycles

---

## Deployment to Render Web Services

### Live Deployment
- **URL**: https://remote-servers-marketplace-test.onrender.com/
- **Status**: Fully operational with all features enabled
- **Database**: Render PostgreSQL with automated backups
- **Monitoring**: Integrated logging and performance monitoring

### Deployment Architecture
- **Web Service**: FastAPI application on Render Free tier
- **Database**: Render PostgreSQL Free tier
- **External Services**: Supabase Auth, Stripe Payments
- **CI/CD**: GitHub Actions with automated testing pre-deployment

### Environment Configuration
- **Secrets Management**: Render environment variables for sensitive data
- **Database Migrations**: Alembic migrations run automatically on startup
- **Health Checks**: Automated health monitoring with `/api/v1/health` endpoint
- **SSL/TLS**: Automatic HTTPS configuration by Render

---

## Maintenance Plan Implementation

### Monitoring Strategy
- **Application Health**: Regular health checks and endpoint monitoring
- **Performance Metrics**: Response times, error rates, and resource utilization
- **Database Monitoring**: Query performance, connection pools, and storage usage
- **External Services**: Stripe and Supabase connectivity monitoring

### Update Management
- **Dependency Updates**: Weekly security updates, monthly version reviews
- **Database Migrations**: Alembic with backward compatibility and rollback capability
- **Security Updates**: Quarterly JWT secret rotation and API key management
- **Deployment Strategy**: Canary deployments with health verification

### Performance Optimization
- **Immediate (0-3 months)**: Booking service refactoring, query optimization
- **Medium-term (3-6 months)**: Async processing implementation, connection pooling
- **Long-term (6-12 months)**: Read replicas, microservices evaluation

### Enhancement Roadmap
- **Phase 1 (Months 1-3)**: Stability and developer experience improvements
- **Phase 2 (Months 4-6)**: Advanced booking and provider features
- **Phase 3 (Months 7-9)**: Enterprise organization management
- **Phase 4 (Months 10-12)**: Platform ecosystem and marketplace features

---

## Git Workflow and Collaboration

### Branch Strategy
- **Main Branch**: Production-ready code, protected with required reviews
- **Dev Branch**: Development integration, CI testing required
- **Stakeholders Branch**: Collaborative work from non-development team members
- **Feature Branches**: Short-lived branches for specific feature development

### Collaboration Patterns
- **Role-Based Contributions**: Clear separation of development and stakeholder roles
- **Pull Request Workflow**: All changes through PRs with required reviews
- **Code Review Culture**: Architectural consistency, test coverage, security considerations
- **Documentation Integration**: Documentation updates required with code changes

### Quality Assurance
- **Pre-commit Hooks**: Syntax validation, import sorting, linting checks
- **CI/CD Pipeline**: Automated testing with coverage enforcement
- **Protected Branches**: No direct commits to main, required status checks
- **Regular Syncs**: Weekly team coordination and architecture discussions

---

# Course Deliverables Mapping (For Grading)

Below is a section that demonstrates fulfilment of the Part 4 project rubric. This section is intentionally separated to maintain industry-standard documentation above.

---

## Stakeholders

### 1. Testing Reports
- **User Acceptance Testing (UAT) Documentation**: Comprehensive UAT test cases located in `docs/user-acceptance-testing/`
- **Testing Feedback Reports**: Detailed reports highlighting identified issues and areas for improvement
- **Stakeholder Validation**: Direct involvement in testing booking workflows, payment processing, and dispute resolution features
- **Documentation**: UAT scenarios covering all major user roles (buyers, providers, admins)

### 2. Maintenance Plan
- **Comprehensive Maintenance Strategy**: Complete maintenance plan covering monitoring, updates, and enhancements
- **Monitoring Guidelines**: Detailed procedures for application health, database performance, and external service monitoring
- **Update Management**: Clear processes for dependency updates, security patches, and database migrations
- **Enhancement Roadmap**: Phased approach for future improvements across four development phases
- **Bug Fix Protocols**: Classification system with defined resolution timelines and procedures
- **Performance Guidelines**: Structured approach to identifying and addressing performance issues

---

## Developers

### 1. Test Cases and Test Reports
- **Comprehensive Test Coverage**: ≥80% line coverage maintained across all 15+ application domains
- **Automated Testing Pipeline**: CI/CD integration with GitHub Actions running on every push and PR
- **Domain-Specific Tests**: Unit and integration tests for each domain (bookings, payments, compliance, etc.)
- **Test Documentation**: Detailed test reports including coverage analysis and test execution results
- **Mock Implementations**: External services (Stripe, Supabase) mocked for reliable testing
- **Database Testing**: Isolated test transactions with automatic rollback and factory patterns

### 2. Deployment Documentation
- **Complete Deployment Guide**: Step-by-step documentation for deploying to Render Web Services
- **Environment Configuration**: Detailed instructions for setting up all required environment variables
- **Cloud Platform Setup**: Comprehensive guide for Render PostgreSQL and Web Service configuration
- **External Service Integration**: Instructions for configuring Supabase Auth and Stripe Payments
- **Production Configuration**: SSL/TLS setup, health checks, monitoring configuration
- **Troubleshooting Guide**: Common deployment issues and solutions documented

### 3. Git Documentation
- **Workflow Documentation**: Complete Git workflow documentation including branch strategy and commit standards
- **Commit History Analysis**: Semantic commit messages and regular development patterns documented
- **Pull Request Process**: Detailed PR creation, review, and merging procedures
- **Quality Assurance**: Pre-commit hooks, protected branches, and automated checks documented
- **Version Control Practices**: Repository structure management and conflict resolution protocols

---

## Combined Deliverables

### Updated Git Repository Includes:
- **Complete Source Code**: All 15+ application domains with full functionality
- **Testing Documentation**: 
  - Unit and integration test suites with ≥80% coverage
  - User acceptance testing scenarios and reports
  - Automated test pipeline configuration
- **Deployment Documentation**:
  - Render deployment guide with environment setup
  - Production configuration and troubleshooting
  - External service integration instructions
- **Maintenance Plan**:
  - Comprehensive monitoring strategy
  - Update management procedures
  - Performance optimization roadmap
  - Bug fix and enhancement guidelines
- **Git Documentation**:
  - Complete workflow and collaboration documentation
  - Branch management and version control practices
  - Quality assurance procedures
- **Infrastructure Configuration**:
  - GitHub Actions CI/CD pipeline
  - Docker Compose setup for local development
  - Alembic migration files and procedures
- **Live Deployment**: Fully operational application
- **API Documentation**: Interactive FastAPI documentation available in live deployment at https://remote-servers-marketplace-test.onrender.com/docs
- **Health Monitoring**: Operational health endpoint with real-time status reporting

### Verification of Deliverables:
1. **Live Application**: Accessible at the provided Render URL with all features functional
2. **Test Coverage**: CI pipeline enforces and verifies ≥80% test coverage
3. **Documentation**: All required documentation committed to the repository
4. **Deployment**: Application successfully deployed and running on Render
5. **Collaboration**: Git history demonstrates team collaboration and workflow adherence
6. **Maintenance**: Comprehensive plan for ongoing support and enhancement