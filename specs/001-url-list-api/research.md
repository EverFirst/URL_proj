# Research: URL List Management API

**Date**: 2025-11-07
**Feature**: URL List Management API
**Purpose**: Technology best practices, architecture patterns, and implementation guidance

## Technology Stack Decisions

### FastAPI 0.104+ Best Practices

**Decision**: Use FastAPI 0.104+ with async/await for all endpoints

**Rationale**:
- Built-in OpenAPI documentation generation (FR-038 requirement)
- Pydantic v2 integration for automatic validation (FR-034, FR-035 requirements)
- Dependency injection system supports Repository pattern and Service layer
- Async support improves throughput under concurrent requests
- Type hints enforced at framework level (Constitution requirement)

**Best Practices**:
- Use `APIRouter` for organizing endpoints by resource (/lists, /urls, /public)
- Leverage `Depends()` for injecting repositories and services
- Return Pydantic models directly from endpoints for automatic serialization
- Use `HTTPException` with appropriate status codes (404, 400, 422, 500)
- Enable CORS if needed via `CORSMiddleware`

**Alternatives Considered**:
- Flask + Flask-RESTful: Rejected - no built-in validation, manual OpenAPI generation, less type-safe
- Django REST Framework: Rejected - heavyweight for API-only project, ORM tightly coupled to framework

### SQLAlchemy 2.0+ with Alembic

**Decision**: SQLAlchemy 2.0 ORM with declarative models, Alembic for migrations

**Rationale**:
- SQLAlchemy 2.0 introduces modern async support and better type hints
- Declarative Base allows clean ORM model definitions
- Relationship cascade support for FR-009 (delete list → delete URLs)
- Alembic provides version-controlled schema migrations
- PostgreSQL compatibility (future production deployment)

**Best Practices**:
- Use `relationship()` with `cascade="all, delete-orphan"` for list→URLs
- Define unique constraints at database level (slug uniqueness - FR-032)
- Use `Index` for frequently queried columns (slug, status)
- Separate ORM models (`infrastructure/models.py`) from domain entities
- Use `sessionmaker` with scoped sessions for thread safety

**Schema Design Patterns**:
```python
# URLList ORM model
class URLListModel(Base):
    __tablename__ = "url_lists"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)  # FR-033: max 200 chars
    slug = Column(String(50), unique=True, nullable=True, index=True)  # FR-031: 3-50 chars, unique
    status = Column(Enum("draft", "published"), default="draft", nullable=False)  # FR-022, FR-023
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    urls = relationship("URLItemModel", back_populates="list", cascade="all, delete-orphan")

# URLItem ORM model
class URLItemModel(Base):
    __tablename__ = "url_items"

    id = Column(Integer, primary_key=True)
    list_id = Column(Integer, ForeignKey("url_lists.id"), nullable=False, index=True)
    url = Column(String(2048), nullable=False)  # FR-029: max 2048 chars
    title = Column(String(200), nullable=True)  # FR-011: optional title
    created_at = Column(DateTime, default=func.now())

    list = relationship("URLListModel", back_populates="urls")
```

**Alternatives Considered**:
- Raw SQL with aiosqlite: Rejected - manual query building error-prone, no migration support
- Tortoise ORM: Rejected - less mature than SQLAlchemy, smaller ecosystem

### Repository Pattern Implementation

**Decision**: Interface-based repositories with SQLAlchemy implementations

**Rationale**:
- User explicitly requested Repository pattern
- Enables service layer to depend on abstractions (dependency inversion)
- Facilitates unit testing with mock repositories
- Isolates SQLAlchemy details from business logic
- Supports future PostgreSQL migration without service layer changes

**Best Practices**:
```python
# Base repository interface (infrastructure/repositories/base.py)
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')

class BaseRepository(Generic[T], ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        pass

    @abstractmethod
    def create(self, entity: T) -> T:
        pass

    @abstractmethod
    def update(self, entity: T) -> T:
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass

# ListRepository interface (infrastructure/repositories/list_repository.py)
class IListRepository(BaseRepository[URLList]):
    @abstractmethod
    def get_by_slug(self, slug: str) -> Optional[URLList]:
        pass

    @abstractmethod
    def slug_exists(self, slug: str, exclude_id: Optional[int] = None) -> bool:
        pass

# SQLAlchemy implementation
class SQLAlchemyListRepository(IListRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_slug(self, slug: str) -> Optional[URLList]:
        model = self.session.query(URLListModel).filter(URLListModel.slug == slug).first()
        return self._to_domain(model) if model else None

    # ... other methods with ORM→domain mapping
```

**Alternatives Considered**:
- Direct service→ORM access: Rejected per constitution guidance (tight coupling, hard to test)
- Generic repository only: Rejected - need slug-specific queries (get_by_slug, slug_exists)

### Service Layer Architecture

**Decision**: Service classes encapsulating business logic with injected repositories

**Rationale**:
- User requested Service Layer + Dependency Injection
- Complex business rules: state transitions, slug validation, cascade operations
- Transaction boundary management (list + URLs modifications)
- Centralizes validation logic (FR-034 through FR-037)

**Best Practices**:
```python
# ListService (domain/services/list_service.py)
class ListService:
    def __init__(self, list_repo: IListRepository, url_repo: IURLRepository):
        self.list_repo = list_repo
        self.url_repo = url_repo

    def create_list(self, title: str) -> URLList:
        if not title or len(title) > 200:
            raise ValidationError("Title must be 1-200 characters")  # FR-033, FR-034

        url_list = URLList(title=title, status="draft")  # FR-022
        return self.list_repo.create(url_list)

    def publish_list(self, list_id: int) -> URLList:
        url_list = self.list_repo.get_by_id(list_id)
        if not url_list:
            raise NotFoundError(f"List {list_id} not found")  # FR-036

        url_list.status = "published"  # FR-024
        return self.list_repo.update(url_list)

    def set_slug(self, list_id: int, slug: str) -> URLList:
        # Validate slug format: FR-030, FR-031
        if not re.match(r'^[a-z0-9-]{3,50}$', slug):
            raise ValidationError("Slug must be 3-50 chars, lowercase alphanumeric and hyphens")

        # Check uniqueness: FR-032
        if self.list_repo.slug_exists(slug, exclude_id=list_id):
            raise ValidationError(f"Slug '{slug}' already exists")

        url_list = self.list_repo.get_by_id(list_id)
        if not url_list:
            raise NotFoundError(f"List {list_id} not found")

        url_list.slug = slug
        return self.list_repo.update(url_list)
```

**Alternatives Considered**:
- Anemic domain model with fat controllers: Rejected - violates SRP, duplicates validation logic
- Domain-driven design with rich entities: Rejected - overkill for CRUD-heavy feature

### Pydantic v2 Validation

**Decision**: Pydantic v2 models for all request/response validation

**Rationale**:
- Constitution mandates Pydantic for validation
- Automatic OpenAPI schema generation
- Field validators for complex rules (URL format, slug pattern)
- Serialization/deserialization with type safety

**Best Practices**:
```python
# Request schemas (api/schemas/list_schemas.py)
from pydantic import BaseModel, Field, field_validator
import re

class ListCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)  # FR-033, FR-034

class ListUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = Field(None, min_length=3, max_length=50)
    status: Optional[Literal["draft", "published"]] = None

    @field_validator('slug')
    def validate_slug(cls, v):
        if v and not re.match(r'^[a-z0-9-]+$', v):  # FR-030
            raise ValueError("Slug must contain only lowercase letters, numbers, and hyphens")
        return v

class URLCreateRequest(BaseModel):
    url: str = Field(..., max_length=2048)
    title: Optional[str] = Field(None, max_length=200)

    @field_validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):  # FR-028
            raise ValueError("URL must start with http:// or https://")
        if len(v) > 2048:  # FR-029
            raise ValueError("URL must be 2048 characters or less")
        return v

# Response schemas
class URLItemResponse(BaseModel):
    id: int
    url: str
    title: Optional[str]
    created_at: datetime

class ListResponse(BaseModel):
    id: int
    title: str
    slug: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    urls: List[URLItemResponse] = []

    class Config:
        from_attributes = True  # Pydantic v2: enable ORM mode
```

**Alternatives Considered**:
- Marshmallow: Rejected - less integrated with FastAPI, manual OpenAPI generation
- Manual validation: Rejected - error-prone, doesn't generate API docs

### Testing Strategy

**Decision**: Three-tier testing (Unit / Integration / Contract) with pytest + httpx

**Rationale**:
- Constitution requires 70% coverage
- User specified pytest + httpx
- Unit tests isolate services/repositories with mocks
- Integration tests verify end-to-end workflows
- Contract tests ensure OpenAPI compliance

**Test Organization**:
```
tests/
├── conftest.py              # Shared fixtures
│   - test_db: In-memory SQLite database
│   - test_client: httpx.AsyncClient with FastAPI app
│   - mock_repositories: Mock implementations for unit tests
├── contract/
│   └── test_api_contracts.py  # Validates OpenAPI spec matches actual responses
├── integration/
│   ├── test_list_workflows.py   # User Story 1: Create/Read/Update/Delete lists
│   ├── test_url_workflows.py    # User Story 2: Add/manage URLs in lists
│   └── test_public_access.py    # User Story 3: Slug-based public access
└── unit/
    ├── services/
    │   ├── test_list_service.py   # Business logic tests with mock repos
    │   └── test_url_service.py
    └── repositories/
        ├── test_list_repository.py  # Data access tests with test DB
        └── test_url_repository.py
```

**Best Practices**:
- Use `pytest.fixture` with scope="function" for test DB isolation
- Leverage `httpx.AsyncClient` for async endpoint testing
- Mock external dependencies in unit tests
- Test edge cases from spec (empty title, invalid slug, duplicate slug, non-existent resources)
- Measure coverage with `pytest --cov=src --cov-report=term-missing`

**Alternatives Considered**:
- unittest: Rejected - pytest fixtures more powerful, better async support
- TestClient (Starlette): Rejected - httpx more flexible, real async support

### Dependency Injection Pattern

**Decision**: FastAPI `Depends()` with factory functions

**Rationale**:
- FastAPI native DI system
- Clean separation of concerns
- Easy to override dependencies in tests
- Singleton services with request-scoped repositories

**Implementation**:
```python
# api/dependencies.py
from fastapi import Depends
from sqlalchemy.orm import Session
from infrastructure.database import get_db
from infrastructure.repositories import SQLAlchemyListRepository, SQLAlchemyURLRepository
from domain.services import ListService, URLService

def get_list_repository(db: Session = Depends(get_db)):
    return SQLAlchemyListRepository(db)

def get_url_repository(db: Session = Depends(get_db)):
    return SQLAlchemyURLRepository(db)

def get_list_service(
    list_repo: IListRepository = Depends(get_list_repository),
    url_repo: IURLRepository = Depends(get_url_repository)
):
    return ListService(list_repo, url_repo)

# Usage in routes (api/routes/lists.py)
@router.post("/lists", response_model=ListResponse, status_code=201)
def create_list(
    request: ListCreateRequest,
    service: ListService = Depends(get_list_service)
):
    url_list = service.create_list(request.title)
    return url_list
```

**Alternatives Considered**:
- Manual dependency instantiation: Rejected - not testable, violates DIP
- dependency-injector library: Rejected - FastAPI's built-in DI sufficient for project scope

## Implementation Guidance

### Error Handling Strategy

**Decision**: Custom exception hierarchy with FastAPI exception handlers

**Pattern**:
```python
# domain/exceptions.py
class DomainException(Exception):
    """Base exception for domain errors"""
    pass

class NotFoundError(DomainException):
    """Resource not found (maps to 404)"""
    pass

class ValidationError(DomainException):
    """Validation failed (maps to 400)"""
    pass

class ConflictError(DomainException):
    """Duplicate resource (maps to 409)"""
    pass

# main.py - register handlers
@app.exception_handler(NotFoundError)
def handle_not_found(request, exc):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(ValidationError)
def handle_validation_error(request, exc):
    return JSONResponse(status_code=400, content={"detail": str(exc)})
```

### Logging Configuration

**Decision**: Structured JSON logging with request context

**Pattern**:
```python
# core/logging.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        return json.dumps(log_data)

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path} - {response.status_code}")
    return response
```

### Database Migration Workflow

**Decision**: Alembic with auto-generate from ORM models

**Commands**:
```bash
# Initialize Alembic
alembic init alembic

# Generate migration from model changes
alembic revision --autogenerate -m "create url_lists and url_items tables"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Performance Considerations

### Database Indexing

**Indexes to Create**:
- `url_lists.slug` (unique index for slug lookups - FR-017)
- `url_lists.status` (index for filtering published lists)
- `url_items.list_id` (foreign key index for joins)
- `url_items.created_at` (for ordering - FR-014)

### Query Optimization

**N+1 Prevention**:
```python
# Use joinedload for eager loading
from sqlalchemy.orm import joinedload

def get_list_with_urls(self, list_id: int) -> Optional[URLList]:
    model = (self.session.query(URLListModel)
             .options(joinedload(URLListModel.urls))
             .filter(URLListModel.id == list_id)
             .first())
    return self._to_domain(model) if model else None
```

### Response Time Targets

- List CRUD operations: <100ms (single DB query)
- List with URLs retrieval: <500ms for 100 URLs (eager loading)
- Slug lookup: <200ms (indexed query)
- URL add/delete: <100ms (single insert/delete)

## Summary

All technical unknowns resolved. Stack: FastAPI 0.104+, SQLAlchemy 2.0+, Pydantic v2, pytest + httpx, Alembic. Architecture: Three-layer (API/Domain/Infrastructure) with Repository pattern and Service layer. Testing: Unit (mocked), Integration (test DB), Contract (OpenAPI validation). 70% coverage enforced via pytest-cov. Ready for Phase 1 design (data model + contracts).
