## Deployment Steps

### Step 1: Create PostgreSQL Database on Render

1. Log into Render Dashboard
2. Click "New +" and select "PostgreSQL"
3. Configure database:
   - Name: `remote-servers-marketplace-db`
   - Database: `marketplace`
   - User: `marketplace_user`
   - Region: Choose closest to your users
   - Instance Type: Start with Free (upgrade as needed)
4. Click "Create Database"
5. Wait for provisioning (2-3 minutes)
6. Copy the Internal Database URL from the database dashboard

### Step 2: Create Web Service on Render

1. In Render Dashboard, click "New +" and select "Web Service"
2. Connect your GitHub repository
3. Configure the service:

Basic Settings
   - Name: `remote-servers-marketplace`
   - Environment: `Python`
   - Region: Same as database region
   - Branch: `main` (or your deployment branch)
   - Root Directory: `.` (repository root)

Build Settings
   - Build Command:
```bash
pip install -r requirements.txt
```

   - Start Command:
```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 10000
```

Instance Settings
   - Instance Type: Free (0.1 CPU, 512 MB RAM)
   - Auto-Deploy: Enable for automatic deployments on push

### Step 3: Configure Environment Variables

In the Web Service dashboard:

1. Navigate to "Environment" tab
2. Add each required environment variable:
   - `DATABASE_URL`: Paste the Internal Database URL from Step 1
   - `PYTHON_VERSION`: `3.12.0`
   - `STRIPE_PUBLISHABLE_KEY`: Your Stripe publishable key
   - `STRIPE_SECRET_KEY`: Your Stripe secret key
   - `STRIPE_WEBHOOK_SECRET`: Your Stripe webhook signing secret
   - `SUPABASE_ANON_KEY`: Your Supabase anonymous key
   - `SUPABASE_JWT_SECRET`: Your Supabase JWT secret
   - `SUPABASE_URL`: Your Supabase project URL
   - `USE_REAL_STRIPE`: true
3. Click "Save Changes"

### Step 4: Initial Deployment

1. Click "Manual Deploy" > "Deploy latest commit"
2. Monitor deployment logs for:
   - Dependencies installation
   - Database migration completion
   - Application startup
3. Verify deployment completes successfully (green status)

### Step 5: Verify Deployment

1. Health Check: Visit `https://your-service.onrender.com/api/v1/health`
   - Expected response: `{"status": "ok"}`
2. Database Connection: Check logs for successful database connection
   - No SQLAlchemy connection errors
3. API Endpoints: Test basic endpoints:
   - `GET /api/v1/listings` - Should return listings (may be empty)
   - `GET /` - Should serve frontend homepage

### Step 6: Configure Stripe Webhooks

1. Update Stripe Dashboard webhook endpoint:
   - URL: `https://your-service.onrender.com/api/v1/payments/webhooks/stripe`
2. Test webhook delivery from Stripe Dashboard
   - Send test event to verify endpoint works
   - Check Render logs for webhook processing

## Post-Deployment Configuration

### 1. Database Migrations Management

The application automatically runs migrations on startup. For manual migration control:

1. Access Render Shell (if needed):
```bash
# In Render Dashboard, use Shell feature if available
alembic upgrade head
```

2. To create new migrations in development:
```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### 2. Monitoring and Logs

Application Logs
   - Access via Render Dashboard > Service > Logs
   - Logs include:
     - Application startup messages
     - API request/response logging
     - Database operations
     - Error messages and stack traces

Performance Monitoring
   - Render provides basic metrics:
     - CPU usage
     - Memory usage
     - Request count
     - Error rates

### 3. Scaling Considerations
Free Tier Limitations
   - Web Service: 750 free hours/month, auto-sleeps after 15 minutes inactivity
   - Database: Limited to 1GB storage, basic performance

Upgrade Path

When traffic increases:
1. Upgrade Web Service to Starter plan ($7/month)
2. Upgrade Database to Starter plan ($7/month)
3. Consider adding Redis for caching ($5/month)

### 4. Backup Strategy

Database Backups

Render provides:
   - Daily automated backups (7-day retention on Free tier)
   - Manual backup capability
   - Backup restoration via dashboard

Recommended Backup Procedure
1. Weekly verification of backup integrity
2. Monthly test restoration in staging environment
3. Document restoration procedure

### 5. Security Configuration

SSL/TLS
   - Render provides automatic HTTPS with Let's Encrypt
   - No additional configuration needed

Secret Management
   - Use Render's built-in environment variable encryption
   - Never commit secrets to version control
   - Rotate secrets periodically (recommended quarterly)

## Troubleshooting Guide

### Common Issues and Solutions

1. Application Fails to Start

Symptoms: Deployment shows "Failed" status

Solutions:
   - Check build logs for dependency installation errors
   - Verify Python version compatibility
   - Ensure `requirements.txt` is complete and valid

2. Database Connection Errors

Symptoms: SQLAlchemy connection timeouts or authentication errors

Solutions:
   - Verify DATABASE_URL is correct and accessible
   - Check PostgreSQL service is running
   - Ensure network connectivity between services

3. Migration Failures

Symptoms: Alembic errors during startup

Solutions:
   - Check migration history consistency
   - Verify database user has necessary permissions
   - Run migrations manually via shell

4. Stripe Webhook Failures

Symptoms: Payments process but no confirmation

Solutions:
   - Verify webhook URL in Stripe Dashboard
   - Check STRIPE_WEBHOOK_SECRET matches
   - Monitor webhook logs in Render

5. Memory Issues

Symptoms: Application crashes or becomes unresponsive

Solutions:
   - Upgrade to larger instance type
   - Optimize database queries
   - Implement connection pooling

## Maintenance Procedures

### Regular Maintenance Tasks

Daily
   - Monitor application logs for errors
   - Check database connection health
   - Verify external service connectivity (Stripe, Supabase)

Weekly
   - Review performance metrics
   - Check storage usage (database and disk)
   - Test critical user flows (booking, payment)

Monthly
   - Rotate security credentials
   - Update dependencies (security patches)
   - Review and clean up logs
   - Test backup restoration

### Update Procedures

Code Updates

1. Push changes to main branch
2. Render automatically deploys (if auto-deploy enabled)
3. Monitor deployment logs
4. Verify application functionality

Database Schema Changes

1. Create Alembic migration in development
2. Test migration locally
3. Deploy code changes
4. Migration runs automatically on startup

Dependency Updates
1. Update requirements.txt
2. Test locally with updated dependencies
3. Deploy to Render
4. Monitor for compatibility issues

## Cost Management

### Free Tier Usage
   - Web Service: 750 hours/month (approximately 31 days)
   - Database: Always free (with limitations)
   - Monitor usage in Render Dashboard > Usage

### Upgrade Triggers

Consider upgrading when:
   - Consistent user traffic (no more auto-sleep)
   - Database storage exceeds 500MB
   - Performance degradation observed
   - Business revenue justifies investment

## Support and Resources

### Render Documentation

https://render.com/docs
https://render.com/docs/postgresql-creating-connecting

# Environment Setup and Configuration Guide

## Initial Setup Process

### Step 1: Repository Verification

Before deployment, verify your repository structure matches the expected layout:

```
├── app/
│ ├── main.py # FastAPI entry point
│ ├── config.py # Configuration settings
│ ├── database.py # Database connection
│ └── [domain folders]/ # All domain modules
├── requirements.txt # Python dependencies
├── alembic.ini # Database migration config
├── alembic/ # Migration scripts
├── frontend/ # Frontend templates and static files
└── tests/ # Test suite
```

### Step 2: Dependency Management

#### Required Python Packages
The `requirements.txt` file must include:

```txt
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.4.1
python-jose[cryptography]==3.3.0
python-dotenv==1.0.0
stripe==7.6.1
jinja2==3.1.2
pytest==7.4.3
pytest-cov==4.1.0
email-validator
black==24.10.0
ruff==0.7.3
mypy==1.11.2
PyJWT>=2.9.0
stripe==14.0.1
```

Version Compatibility
   - Python 3.12.0 (specified in PYTHON_VERSION environment variable)
   - PostgreSQL 16 (Render's default for new databases)
   - All packages compatible with Python 3.12

### Step 3: External Service Configuration

#### A. Supabase Authentication Setup

1. Create Supabase Project:
   - Visit supabase.com
   - Create new organization and project
   - Select region closest to your users

2. Configure Authentication:
   - Navigate to Authentication > Providers
   - Enable Email provider
   - Configure email templates as needed

3. Retrieve Credentials:
   - Project Settings > API
   - Copy:
     - Project URL → `SUPABASE_URL`
     - Anonymous Key → `SUPABASE_ANON_KEY`
     - JWT Secret → `SUPABASE_JWT_SECRET`

4. Configure JWT Settings:
   - Ensure JWT expiry matches application expectations (default 3600 seconds)
   - Verify algorithm is HS256 (compatible with python-jose)

#### B. Stripe Payment Integration

1. Stripe Account Setup:
   - Sign up at stripe.com
   - Access Dashboard > Developers
   - Enable Test Mode for development

2. API Keys Generation:
   - Developers > API Keys
   - Copy:
     - Publishable Key → `STRIPE_PUBLISHABLE_KEY`
     - Secret Key → `STRIPE_SECRET_KEY`

3. Webhook Configuration:
   - Developers > Webhooks
   - Add endpoint: `https://[your-render-url]/api/v1/payments/webhooks/stripe`
   - Select events:
     - `checkout.session.completed`
     - `payment_intent.succeeded`
     - `payment_intent.payment_failed`
   - Copy Signing Secret → `STRIPE_WEBHOOK_SECRET`

4. Test Data:
   - Use test card: 4242 4242 4242 4242
   - Any future expiry date
   - Any 3-digit CVC
   - Any valid ZIP code

### Step 4: Database Configuration

#### A. Local Development Database

1. Install PostgreSQL:
```bash
# macOS
brew install postgresql@16

# Ubuntu/Debian
sudo apt install postgresql-16

# Windows
# Download installer from postgresql.org
```

2. Create Local Database:
```bash
createdb marketplace_dev
psql marketplace_dev
```

3. Configure Connection:

Update .env file:
```bash
DATABASE_URL=postgresql://localhost:5432/marketplace_dev
```

#### B. Render Production Database
1. Automatic Configuration:
Render provides DATABASE_URL automatically when PostgreSQL service is linked

2. Connection Pooling:
The application uses SQLAlchemy's connection pooling:
   - Default pool size: 5 connections
   - Max overflow: 10 connections
   - Timeout: 30 seconds

### Step 5: Environment Variables Configuration

Complete Environment Variables List

Create a .env file for local development:
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/marketplace_dev
TEST_DATABASE_URL=postgresql://user:password@localhost:5432/marketplace_test

# Python
PYTHON_VERSION=3.12.0   # optional but recommended

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret

# Stripe
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxxxxx
STRIPE_SECRET_KEY=sk_test_xxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxx
USE_REAL_STRIPE=false  # true for production

# Application
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

Render Environment Variables Setup

In Render Dashboard, add each variable:

1. Navigate to Environment tab
2. Click "Add Environment Variable"
3. Enter name and value
4. Repeat for all required variables
5. Click "Save Changes"

Important: Mark sensitive values as "Secret" when applicable

### Step 6: Build and Runtime Configuration

#### A. Build Process

The Render build process executes:
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Verify Python version
python --version  # Should match PYTHON_VERSION

# 3. Check application structure
ls -la app/       # Should show main.py and domain directories
```

#### B. Startup Process

The application starts with:

```bash
# 1. Run database migrations
alembic upgrade head

# 2. Start FastAPI application
uvicorn app.main:app --host 0.0.0.0 --port 10000
```

Port Configuration: Render expects applications to listen on port specified in `$PORT` environment variable (default 10000).

### Step 7: Network and Security Configuration

#### A. CORS Configuration
The application is configured for:

```python
# From main.py
FRONTEND_ORIGIN = "https://remote-servers-marketplace-test.onrender.com"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_ORIGIN,
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### B. Security Headers

The application includes:
   - HTTPS enforcement (via Render)
   - Cookie security (HttpOnly, Secure, SameSite=Lax)
   - JWT token validation
   - Input validation via Pydantic schemas

### Step 8: Testing Configuration

#### A. Test Database Setup

1. Create Test Database:
```bash
createdb marketplace_test
```

2. Configure Test Environment:
```bash
TEST_DATABASE_URL=postgresql://localhost:5432/marketplace_test
USE_REAL_STRIPE=false
```

3. Run Tests:
```bash
pytest --cov=app --cov-report=term-missing --cov-report=xml
```

#### B. Continuous Integration

GitHub Actions configuration (`/.github/workflows/ci.yml`):

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: pytest
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/postgres
```

### Step 9: Monitoring Configuration

#### A. Application Health Checks

1. Health Endpoint: `GET /api/v1/health`
   - Returns: `{"status": "ok"}`
   - Checks: Database connectivity, application state

2. Render Health Check:
   - Path: /api/v1/health
   - Interval: 30 seconds
   - Timeout: 10 seconds

#### B. Logging Configuration

The application logs to stdout with levels:
   - `ERROR`: Application errors, payment failures
   - `WARNING`: Deprecation warnings, configuration issues
   - `INFO`: Startup messages, major operations
   - `DEBUG`: Detailed request/response (development only)

### Step 10: Backup and Recovery Configuration

#### A. Database Backups

Render provides automated backups:
   - Frequency: Daily
   - Retention: 7 days (Free tier)
   - Storage: Render-managed

#### B. Manual Backup Procedure

1. Export Database:
```bash
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
```

2. Verify Backup:
```bash
head -n 20 backup*.sql  # Check structure
```

3. Restore Procedure:
```bash
psql $DATABASE_URL < backup_file.sql
```

### Step 11: Maintenance Configuration

#### A. Scheduled Tasks

For future maintenance tasks (cron jobs):
1. Create Cron Job Service in Render
2. Schedule: Use Unix cron syntax
3. Tasks:
   - Daily: Log rotation
   - Weekly: Database maintenance
   - Monthly: Report generation

#### B. Update Procedure

1. Dependency Updates:
```bash
pip list --outdated
pip install --upgrade package-name
pip freeze > requirements.txt
```

2. Database Migrations:
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Step 12: Final Verification Checklist

Before going live:
   - All environment variables configured
   - Database migrations completed successfully
   - Health endpoint responds correctly
   - External services (Stripe, Supabase) connected
   - SSL certificate issued (Render automatic)
   - Domain configured (if using custom domain)
   - Backup procedure tested
   - Monitoring configured
   - Team notified of deployment
   - Documentation updated

### Step 13: Post-Deployment Tasks

1. User Acceptance Testing:
   - Test registration/login flow
   - Test booking creation
   - Test payment processing
   - Test dispute resolution

2. Performance Baseline:
   - Record response times for key endpoints
   - Measure database query performance
   - Monitor resource utilization

3. Security Review:
   - Verify no sensitive data in logs
   - Confirm HTTPS enforcement
   - Validate authentication flows

## Troubleshooting Configuration Issues

### Common Configuration Problems

1. Missing Environment Variables:
   - Symptom: Application fails to start
   - Solution: Verify all required variables are set in Render

2. Database Connection Issues:
   - Symptom: SQLAlchemy connection errors
   - Solution: Check `DATABASE_URL` format and accessibility

3. CORS Errors:
   - Symptom: Frontend cannot call API
   - Solution: Verify `FRONTEND_ORIGIN` matches deployed URL

4. JWT Validation Failures:
   - Symptom: Authentication errors
   - Solution: Ensure `SUPABASE_JWT_SECRET` matches Supabase project