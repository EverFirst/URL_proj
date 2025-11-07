# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

URL List Management API - A RESTful API for managing URL collections with public sharing capabilities. Built with FastAPI, SQLAlchemy, and follows three-layer architecture (API/Domain/Infrastructure) with Repository pattern and Service layer.

## Technology Stack

- **Runtime**: Python 3.11+
- **Framework**: FastAPI 0.104+ (async/await)
- **ORM**: SQLAlchemy 2.0+ with Alembic migrations
- **Validation**: Pydantic v2
- **Database**: SQLite (dev), PostgreSQL-ready (production)
- **Testing**: pytest + httpx, pytest-cov (70% minimum coverage)

## Architecture

### Three-Layer Structure

```
src/
├── api/                    # FastAPI routes, Pydantic schemas, DI container
│   ├── routes/            # Endpoint handlers (lists.py, urls.py, public.py)
│   ├── schemas/           # Request/response models (Pydantic)
│   └── dependencies.py    # Dependency injection setup
├── domain/                 # Business logic (framework-independent)
│   ├── services/          # Business rules, validation, state transitions
│   ├── models.py          # Domain entities (dataclasses, not ORM)
│   └── exceptions.py      # Domain-specific exceptions
└── infrastructure/         # External concerns (database, repositories)
    ├── repositories/      # Data access interfaces + SQLAlchemy implementations
    ├── models.py          # ORM models (SQLAlchemy)
    └── database.py        # Session management

tests/
├── contract/              # OpenAPI compliance validation
├── integration/           # End-to-end API tests (test DB)
└── unit/                  # Service/repository tests (mocked dependencies)
```

**Key Architectural Decisions**:
- **Repository Pattern**: Abstracts data access, enables testing without database, supports future PostgreSQL migration
- **Service Layer**: Encapsulates business logic (state transitions, validation orchestration, transaction boundaries)
- **Dependency Injection**: FastAPI `Depends()` for injecting repositories into services, services into routes

### Data Model

Two entities with 1:N relationship:
- **URLList**: id, title (required, 1-200 chars), slug (optional, unique, 3-50 chars, pattern: `^[a-z0-9-]+$`), status (enum: draft/published), timestamps
- **URLItem**: id, list_id (FK), url (http/https, max 2048 chars), title (optional, max 200 chars), created_at

**State Machine**: draft ↔ published (lists can be published with/without slug)
**Cascade Delete**: Deleting URLList auto-deletes all URLItems

## Essential Commands

### Development Server

```bash
# Start dev server with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Poetry variant
poetry run uvicorn src.main:app --reload
```

Access:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- OpenAPI spec: http://localhost:8000/openapi.json

### Database Migrations

```bash
# Generate migration from ORM model changes
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1

# Check current version
alembic current

# Reset database (DANGER - deletes all data)
rm url_lists.db && alembic upgrade head
```

### Testing

```bash
# Run all tests with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test types
pytest tests/unit/                    # Unit tests only
pytest tests/integration/             # Integration tests only
pytest tests/contract/                # Contract tests only

# Run single test file
pytest tests/integration/test_list_workflows.py

# Run single test function
pytest tests/unit/services/test_list_service.py::test_create_list

# Generate HTML coverage report
pytest --cov=src --cov-report=html     # Opens htmlcov/index.html
```

**Coverage Requirements**: MUST maintain ≥70% coverage per constitution

### Linting & Formatting

```bash
# Lint with ruff
ruff check src tests

# Auto-fix issues
ruff check --fix src tests

# Format with Black
black src tests

# Type checking (if mypy installed)
mypy src
```

## Constitutional Requirements

The `.specify/memory/constitution.md` file defines mandatory rules. Key requirements:

### Mandatory
- **RESTful Design**: Resource-oriented URLs, standard HTTP methods, appropriate status codes
- **Type Hints**: REQUIRED on ALL functions
- **Pydantic Validation**: ALL inputs MUST be validated (no unvalidated user input reaches business logic)
- **Test Coverage**: ≥70% (measured via pytest-cov)
- **Performance**: <500ms P95 response time
- **Logging**: ALL endpoints log timestamp/method/path/status; ALL errors logged with stack traces
- **Conventional Commits**: `type(scope): description` format (feat, fix, docs, test, refactor, chore)

### Error Handling Standards
- 404 Not Found: Non-existent resources
- 400 Bad Request: Business rule violations (empty title, duplicate slug)
- 422 Unprocessable Entity: Format validation failures (invalid slug pattern, URL not http/https)
- 409 Conflict: Unique constraint violations (slug already exists)
- 500 Internal Server Error: Unexpected failures

### Code Review Checklist
- Type hints on all functions
- Pydantic validation on all API inputs
- Tests included for new functionality
- No sensitive data in logs/responses (production)
- Business logic in services (not controllers)
- Data access via repositories (not direct ORM in services)

## Feature Development Workflow

This project uses SpecKit workflow (commands in `.claude/commands/`):

1. **Specify**: `/speckit.specify` - Create feature spec with user stories, requirements, success criteria
2. **Clarify**: `/speckit.clarify` - Resolve ambiguities (max 5 questions)
3. **Plan**: `/speckit.plan` - Generate technical design (architecture, data model, API contracts)
4. **Tasks**: `/speckit.tasks` - Break down into implementation tasks
5. **Implement**: `/speckit.implement` - Execute tasks with TDD approach

Current features are in `specs/{number}-{feature-name}/` with:
- `spec.md`: Feature specification (WHAT to build)
- `plan.md`: Technical implementation plan (HOW to build)
- `data-model.md`: Entity design
- `contracts/openapi.yaml`: API specification
- `quickstart.md`: Development setup guide

## API Endpoints (from OpenAPI spec)

**Lists Resource** (`/lists`):
- `POST /lists` - Create list (title required)
- `GET /lists` - Get all lists (creation order, no pagination)
- `GET /lists/{id}` - Get specific list with URLs
- `PATCH /lists/{id}` - Update title/slug/status
- `DELETE /lists/{id}` - Delete list + cascade delete URLs

**URLs Resource** (`/lists/{id}/urls`):
- `POST /lists/{id}/urls` - Add URL to list
- `GET /lists/{id}/urls` - Get URLs in list (creation order)
- `DELETE /lists/{id}/urls/{url_id}` - Remove URL from list

**Public Access** (`/public/{slug}`):
- `GET /public/{slug}` - Access published list by slug (404 if draft or no slug)

## Validation Rules (Reference)

**URLList**:
- title: 1-200 chars, NOT NULL
- slug: 3-50 chars, pattern `^[a-z0-9-]+$`, UNIQUE, nullable
- status: enum("draft", "published")

**URLItem**:
- url: starts with http:// or https://, max 2048 chars
- title: max 200 chars, nullable

## Testing Patterns

**Unit Tests** (services/repositories):
```python
# Mock repositories in service tests
mock_list_repo = Mock(spec=IListRepository)
service = ListService(mock_list_repo, mock_url_repo)

# Use test DB for repository tests
def test_list_repository(test_db):  # test_db fixture in conftest.py
    repo = SQLAlchemyListRepository(test_db)
```

**Integration Tests** (end-to-end):
```python
def test_create_list(test_client):  # httpx.AsyncClient fixture
    response = test_client.post("/lists", json={"title": "Test"})
    assert response.status_code == 201
```

**Contract Tests** (OpenAPI validation):
- Verify responses match OpenAPI schema
- Test all documented status codes
- Validate error response formats

## Dependency Injection Pattern

```python
# repositories injected via Depends()
def get_list_repository(db: Session = Depends(get_db)):
    return SQLAlchemyListRepository(db)

# services injected with repositories
def get_list_service(
    list_repo: IListRepository = Depends(get_list_repository),
    url_repo: IURLRepository = Depends(get_url_repository)
):
    return ListService(list_repo, url_repo)

# routes use services
@router.post("/lists")
def create_list(
    request: ListCreateRequest,
    service: ListService = Depends(get_list_service)
):
    return service.create_list(request.title)
```

Override in tests:
```python
app.dependency_overrides[get_list_repository] = lambda: MockListRepository()
```

## Important Implementation Notes

### Publishing Logic
- Lists can be published WITHOUT a slug (not accessible via `/public/{slug}`)
- Draft lists WITH a slug: slug reserved but `/public/{slug}` returns 404
- Published list WITH slug: accessible via `/public/{slug}`

### Ordering
- Lists returned in creation order (oldest first)
- URLs within a list returned in creation order (first added appears first)
- No pagination implemented (full retrieval only)

### State Transitions
- New lists created as "draft" by default
- Can set slug on draft lists (before publishing)
- Can transition: draft ↔ published freely
- Changing slug on published list: old slug immediately invalid

### Cascade Behavior
- DELETE list → automatically deletes all associated URLs
- Implemented via SQLAlchemy `cascade="all, delete-orphan"`
- Database-level foreign key constraint ensures referential integrity

## File Locations

- Feature specs: `specs/{number}-{name}/`
- Constitution: `.specify/memory/constitution.md`
- OpenAPI contract: `specs/001-url-list-api/contracts/openapi.yaml`
- Data model: `specs/001-url-list-api/data-model.md`
- Setup guide: `specs/001-url-list-api/quickstart.md`

<!-- MANUAL ADDITIONS START -->
<!-- Add project-specific notes here that aren't auto-generated -->
<!-- MANUAL ADDITIONS END -->
