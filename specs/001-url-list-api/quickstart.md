# Quickstart: URL List Management API

**Feature**: URL List Management API
**Date**: 2025-11-07
**Purpose**: Development environment setup and workflow guide

## Prerequisites

- Python 3.11 or higher
- pip or Poetry (package management)
- Git
- SQLite (included with Python)
- Code editor (VS Code recommended)

## Initial Setup

### 1. Create Project Structure

```bash
# Navigate to repository root
cd C:\workspace\URL_proj

# Create source directories
mkdir -p src/api/routes src/api/schemas
mkdir -p src/domain/services
mkdir -p src/infrastructure/repositories
mkdir -p src/core
mkdir -p tests/contract tests/integration tests/unit/services tests/unit/repositories
mkdir -p alembic/versions

# Create __init__.py files
touch src/__init__.py
touch src/api/__init__.py src/api/routes/__init__.py src/api/schemas/__init__.py
touch src/domain/__init__.py src/domain/services/__init__.py
touch src/infrastructure/__init__.py src/infrastructure/repositories/__init__.py
touch src/core/__init__.py
touch tests/__init__.py tests/contract/__init__.py tests/integration/__init__.py tests/unit/__init__.py
```

### 2. Install Dependencies

#### Option A: Using pip

Create `requirements.txt`:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.1
```

Install:
```bash
pip install -r requirements.txt
```

#### Option B: Using Poetry (Recommended)

Create `pyproject.toml`:
```toml
[tool.poetry]
name = "url-list-api"
version = "1.0.0"
description = "URL List Management API with FastAPI"
authors = ["Your Name <your.email@example.com>"]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.1"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
sqlalchemy = "^2.0.23"
alembic = "^1.12.1"
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"
python-dotenv = "^1.0.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.3"
pytest-asyncio = "^0.21.1"
pytest-cov = "^4.1.0"
httpx = "^0.25.1"
black = "^23.11.0"
ruff = "^0.1.6"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
addopts = "--cov=src --cov-report=term-missing --cov-report=html"

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/__init__.py"]

[tool.coverage.report]
fail_under = 70
show_missing = true

[tool.black]
line-length = 100
target-version = ['py311']

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W"]
ignore = []

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

Install:
```bash
poetry install
```

### 3. Configure Database

Initialize Alembic:
```bash
alembic init alembic
```

Update `alembic/env.py`:
```python
from src.infrastructure.models import Base  # Import ORM models
target_metadata = Base.metadata
```

Update `alembic.ini`:
```ini
sqlalchemy.url = sqlite:///./url_lists.db
```

### 4. Environment Configuration

Create `.env` file:
```env
# Application
APP_NAME=URL List Management API
DEBUG=True
ENVIRONMENT=development

# Database
DATABASE_URL=sqlite:///./url_lists.db

# API
API_HOST=0.0.0.0
API_PORT=8000
RELOAD=True

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json  # or 'text' for development
```

Create `src/core/config.py`:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "URL List Management API"
    debug: bool = True
    environment: str = "development"

    database_url: str
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    reload: bool = True

    log_level: str = "INFO"
    log_format: str = "json"

    class Config:
        env_file = ".env"

settings = Settings()
```

### 5. Create .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Database
*.db
*.sqlite
*.sqlite3

# Testing
.pytest_cache/
.coverage
htmlcov/
*.cover

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Environment
.env
.env.local

# Logs
*.log
```

## Development Workflow

### 1. Create Database Models

`src/infrastructure/models.py`:
```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class URLListModel(Base):
    __tablename__ = "url_lists"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(50), unique=True, nullable=True, index=True)
    status = Column(Enum("draft", "published", name="status_enum"), default="draft", nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    urls = relationship("URLItemModel", back_populates="list", cascade="all, delete-orphan")

class URLItemModel(Base):
    __tablename__ = "url_items"

    id = Column(Integer, primary_key=True)
    list_id = Column(Integer, ForeignKey("url_lists.id"), nullable=False, index=True)
    url = Column(String(2048), nullable=False)
    title = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    list = relationship("URLListModel", back_populates="urls")
```

### 2. Generate Migration

```bash
alembic revision --autogenerate -m "Create url_lists and url_items tables"
```

Review generated migration in `alembic/versions/`, then apply:
```bash
alembic upgrade head
```

### 3. Run Development Server

```bash
# With uvicorn directly
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or with Poetry
poetry run uvicorn src.main:app --reload
```

Access:
- API: http://localhost:8000
- Interactive docs (Swagger UI): http://localhost:8000/docs
- Alternative docs (ReDoc): http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

### 4. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/integration/test_list_workflows.py

# Run specific test
pytest tests/unit/services/test_list_service.py::test_create_list

# Generate HTML coverage report
pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

### 5. Database Management

```bash
# Check current migration version
alembic current

# Upgrade to latest
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade <revision_id>

# Show migration history
alembic history

# Reset database (DANGER: deletes all data)
rm url_lists.db
alembic upgrade head
```

## Testing the API

### Using Interactive Docs (Recommended for Development)

1. Navigate to http://localhost:8000/docs
2. Expand any endpoint (e.g., POST /lists)
3. Click "Try it out"
4. Fill in request body
5. Click "Execute"
6. View response

### Using curl

```bash
# Create a list
curl -X POST http://localhost:8000/lists \
  -H "Content-Type: application/json" \
  -d '{"title": "My Tools"}'

# Get all lists
curl http://localhost:8000/lists

# Get specific list
curl http://localhost:8000/lists/1

# Update list (set slug)
curl -X PATCH http://localhost:8000/lists/1 \
  -H "Content-Type: application/json" \
  -d '{"slug": "my-tools"}'

# Publish list
curl -X PATCH http://localhost:8000/lists/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "published"}'

# Add URL to list
curl -X POST http://localhost:8000/lists/1/urls \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "title": "Example"}'

# Get URLs in list
curl http://localhost:8000/lists/1/urls

# Access via public slug
curl http://localhost:8000/public/my-tools

# Delete URL
curl -X DELETE http://localhost:8000/lists/1/urls/1

# Delete list
curl -X DELETE http://localhost:8000/lists/1
```

### Using httpx (Python)

```python
import httpx

client = httpx.Client(base_url="http://localhost:8000")

# Create list
response = client.post("/lists", json={"title": "Tech Resources"})
list_data = response.json()
list_id = list_data["id"]

# Add URL
client.post(f"/lists/{list_id}/urls", json={
    "url": "https://github.com",
    "title": "GitHub"
})

# Publish with slug
client.patch(f"/lists/{list_id}", json={
    "slug": "tech-resources",
    "status": "published"
})

# Access via slug
response = client.get("/public/tech-resources")
print(response.json())
```

## Code Quality

### Linting

```bash
# Check with ruff
ruff check src tests

# Auto-fix issues
ruff check --fix src tests
```

### Formatting

```bash
# Check formatting
black --check src tests

# Auto-format
black src tests
```

### Type Checking

```bash
# Install mypy
pip install mypy

# Check types
mypy src
```

## Troubleshooting

### Database locked error
```
Solution: Close all connections to SQLite database, or use `timeout` parameter in connection string
```

### Import errors
```
Solution: Ensure src/ is in PYTHONPATH or run from repository root
```

### Migration conflicts
```
Solution: Delete conflicting migration files, reset database, regenerate migration
```

### Port already in use
```
Solution: Change port in .env or kill process on port 8000
# Windows: netstat -ano | findstr :8000, then taskkill /PID <PID> /F
# Linux: lsof -ti:8000 | xargs kill
```

## Next Steps

1. Implement `/speckit.tasks` to generate task breakdown
2. Follow TDD approach: write tests first, then implement
3. Monitor test coverage (must stay ≥70%)
4. Use interactive docs for manual testing
5. Review logs for debugging (check console output)
6. Commit frequently with conventional commit messages

## Production Deployment (Future)

### Database Migration

1. Switch to PostgreSQL:
   - Update `DATABASE_URL` in `.env`
   - Install `psycopg2-binary`
   - Run migrations with `alembic upgrade head`

2. Environment variables:
   - Set `DEBUG=False`
   - Set `ENVIRONMENT=production`
   - Use strong database credentials

3. Server:
   - Use gunicorn instead of uvicorn dev server
   - Configure reverse proxy (nginx)
   - Enable HTTPS
   - Set up monitoring and logging aggregation

### Performance Tuning

- Add connection pooling (SQLAlchemy)
- Configure caching (Redis for slug lookups)
- Add rate limiting (slowapi)
- Enable response compression
- Monitor with Prometheus/Grafana

## Summary

Development environment ready. Run `uvicorn src.main:app --reload` to start server, visit http://localhost:8000/docs to test API, and execute `pytest` to run tests. Maintain 70% coverage per constitution requirements.
