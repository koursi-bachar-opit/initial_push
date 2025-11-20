# **CI/CD Pipeline Configuration & Setup Details**

This document provides an overview of the continuous integration/continuous deployment (CI/CD) pipeline implemented for this project. It summarizes the architecture of the workflow, migration process, testing process, PostgreSQL service configuration, coverage enforcement, and practical guidelines for modifying or extending the pipeline. The pipeline is implemented using **GitHub Actions** and is defined in `.github/workflows/ci.yml`.

---

## **1. Workflow Overview**

The CI workflow runs automatically on:

- **Pushes** to `main` and `dev`  
- **Pull requests** targeting `main` or `dev`  

The workflow consists of a single job, **`test`**, which performs environment setup, database provisioning, migrations, automated testing, and coverage checks.

---

## **2. GitHub Actions Environment**

### **Runner**
The job executes on:

```
runs-on: ubuntu-latest
```

This ensures a consistent Linux-based environment for Python, PostgreSQL, and all supporting tools.

### **Python Setup**
The pipeline installs Python 3.12 using the official setup action:

```
uses: actions/setup-python@v5
with:
  python-version: '3.12'
```

Dependencies are installed using `pip` and `requirements.txt`.

---

## **3. PostgreSQL Service Configuration**

A PostgreSQL 16 instance is provisioned via GitHub Actions services:

```yaml
services:
  db:
    image: postgres:16
    ports: ['5432:5432']
    env:
      POSTGRES_USER: ${{ secrets.POSTGRES_USER }}
      POSTGRES_PASSWORD: ${{ secrets.POSTGRES_PASSWORD }}
      POSTGRES_DB: ${{ secrets.POSTGRES_DB }}
```

### Notes:
- The database runs inside the GitHub runner's container environment.  
- Credentials are sourced from GitHub **Actions Secrets** (see Section 6).  
- `pg_isready` is used to ensure the service is accepting connections before tests begin.

---

## **4. Database Migrations**

Before running tests, the workflow applies all Alembic migrations:

```yaml
env:
  DATABASE_URL: ${{ env.TEST_DATABASE_URL }}
run: alembic upgrade head
```

### Notes:
- Migrations are always executed against **`TEST_DATABASE_URL`**, not the production or development database.
- This protects against accidental schema changes in non-test environments.

---

## **5. Test Execution and Coverage**

Tests run using `pytest`:

```yaml
env:
  DATABASE_URL: ${{ env.TEST_DATABASE_URL }}
  TEST_DATABASE_URL: ${{ env.TEST_DATABASE_URL }}
run: pytest
```

Test configurations are orchestrated by `pytest.ini` in the project root:

```ini
addopts =
    --cov=app
    --cov-report=term-missing
    --cov-report=xml
    -q
    -ra
    --maxfail=1
    --disable-warnings
...
```

Coverage is then validated by inspecting `coverage.xml`, enforcing a minimum of **80% line coverage**:

```python
cov = float(ET.parse('coverage.xml').getroot().attrib['line-rate'])
if cov < 0.80:
    raise SystemExit(f"Coverage {cov:.1%} below 80%")
```

### Notes:
- If coverage falls below the threshold, the workflow fails and blocks merges.  
- A generated `coverage.xml` is automatically uploaded as an artifact for inspection.

---

## **6. Required Secrets**

The pipeline requires the following GitHub Actions Secrets:

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `TEST_DATABASE_URL`

The workflow begins by failing fast if any required secret is missing, providing strong safety guarantees:

```bash
if [ -z "${!k}" ]; then
  echo "::error::Missing required secret: $k"
  exit 1
fi
```

### Actionable Instruction:
To set or update secrets:

1. Go to **GitHub Repository → Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Add or modify values as required

---

## **7. Coverage Artifact Upload**

Regardless of success or failure, the workflow uploads `coverage.xml` for inspection:

```yaml
uses: actions/upload-artifact@v4
with:
  name: coverage-report
  path: coverage.xml
```

This ensures the team can review coverage history and debug coverage changes over time.

---

## **8. Actionable Instructions for Contributors**

### **Running CI Logic Locally**
To replicate CI locally:

```bash
export TEST_DATABASE_URL=postgresql://...
alembic upgrade head
pytest --cov
```

For full parity, developers can use Docker Compose to run local PostgreSQL.

---

### **Adding a New Pipeline Step**
1. Open `.github/workflows/ci.yml`  
2. Locate the `steps:` section under `jobs.test`  
3. Add a new step, for example:

```yaml
- name: Run lint checks
  run: flake8 .
```

---

### **Modifying Coverage Requirements**
Update the threshold inside the Python block under **Enforce coverage ≥ 80%**:

```python
if cov < 0.85:
```

---

## **9. Summary**

This CI/CD pipeline ensures:

- **Automated testing for any push or pull request to the main and dev branches**  
- **Consistent database migrations in a controlled environment**  
- **Strict minimum coverage enforcement**  
- **Safe handling of secrets and test database environments**  
- **Artifact generation for debugging and validation**

The configuration supports reliability, maintainability, and continuous verification of project behavior, demonstrating disciplined, real-world CI/CD practices suitable for software engineering coursework and industry standards.