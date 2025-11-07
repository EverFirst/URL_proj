# Implementation Plan: URL List Management API

**Branch**: `001-url-list-api` | **Date**: 2025-11-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-url-list-api/spec.md`

## Summary

Build a RESTful API for managing URL collections with public sharing capabilities. Users create lists, populate them with URLs, and optionally publish via unique slugs. Core features include full CRUD operations on lists and URLs, draft/published state management, slug-based public access, and comprehensive input validation. Implementation uses FastAPI with SQLAlchemy ORM, Repository pattern for data access, Service layer for business logic, and achieves 70% test coverage. Data persists to SQLite (development) with PostgreSQL readiness for production.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.104+, SQLAlchemy 2.0+ (ORM), Pydantic v2 (validation), Alembic (migrations)
**Storage**: SQLite (development), PostgreSQL-ready for production
**Testing**: Pytest + httpx (API testing), pytest-cov (coverage measurement)
**Target Platform**: Linux/Windows server (cross-platform)
**Project Type**: Single backend API (no frontend)
**Performance Goals**: <500ms P95 response time, <1s for slug access with 100 URLs
**Constraints**: 70% test coverage minimum, type hints required, OpenAPI auto-docs
**Scale/Scope**: Dozens to hundreds of lists, low-moderate concurrency, no auth system

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Mandatory Compliance

- **RESTful API Design**: Resource-oriented endpoints (`/lists`, `/lists/{id}`, `/lists/{id}/urls`, `/public/{slug}`) with standard HTTP methods
- **Python 3.11+ Runtime**: Specified in user input, aligns with constitution
- **FastAPI Framework**: Specified, meets constitution requirement
- **Pydantic Validation**: All inputs validated via Pydantic v2 models
- **Type Hints**: Required on all functions per constitution
- **OpenAPI Documentation**: Auto-generated via FastAPI (built-in)
- **Test Coverage 70%+**: User input specifies 70%, meets minimum
- **Input Validation**: All FR-028 through FR-037 enforce strict validation
- **Error Handling**: HTTP status codes (FR-036: 404 for not-found, 4xx for validation errors)
- **Data Persistence**: SQLite with file-based storage ensures restart durability (FR-026)

### ⚠️ Optional Patterns - JUSTIFICATION REQUIRED

**Repository Pattern (Optional - Constitution Principle III)**

| Aspect | Evaluation |
|--------|------------|
| **Justification** | User explicitly requested Repository pattern. Feature has clear entity boundaries (URLList, URLItem), multiple data access patterns (by ID, by slug, by status), and cascade delete requirements (FR-009). Repository abstraction enables clean testing, mock injection, and future PostgreSQL migration without business logic changes. |
| **Complexity** | Moderate - adds repository interfaces and implementations but prevents tight coupling to SQLAlchemy throughout service layer |
| **Simpler Alternative Rejected** | Direct SQLAlchemy session usage in services - rejected because it tightly couples business logic to ORM, makes testing harder (requires database for all service tests), and violates dependency inversion. Repository pattern justified by data access complexity and testing needs. |

**Clean Architecture Layers (Optional - Constitution Principle II)**

| Aspect | Evaluation |
|--------|------------|
| **Justification** | User specified Service Layer + Dependency Injection. Feature has distinct concerns: API layer (FastAPI routes), business logic (validation, state transitions), data access (repositories). Layered architecture prevents mixing concerns and enables independent testing. |
| **Complexity** | Moderate - three layers (API/Service/Repository) with clear boundaries |
| **Simpler Alternative Rejected** | Fat controllers with inline database logic - rejected because it creates untestable monolithic route handlers, violates Single Responsibility Principle, and makes

 business rule changes require touching API layer. Service layer justified by state management complexity (draft↔published transitions, slug uniqueness enforcement). |

### ✅ Constitution Gates Passed

- **Observability**: All endpoints will log timestamp, method, path, status (Constitution: Quality Standards)
- **Performance**: <500ms P95 aligns with <500ms constitution requirement
- **TDD Recommended**: Tests required per spec (FR-038/039), pytest framework specified
- **Conventional Commits**: Will be enforced during implementation (governance requirement)

**Verdict**: **APPROVED** - Repository Pattern and Service Layer justified by data access complexity, testing requirements, and explicit user specification. No violations requiring mitigation.

## Project Structure

### Documentation (this feature)

```text
specs/001-url-list-api/
├── plan.md              # This file (/speckit.plan command output)
├── spec.md              # Feature specification (completed)
├── research.md          # Phase 0 output (technology best practices)
├── data-model.md        # Phase 1 output (entity design)
├── quickstart.md        # Phase 1 output (development setup guide)
├── contracts/           # Phase 1 output (OpenAPI spec)
│   └── openapi.yaml
├── checklists/          # Quality validation
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── api/                 # FastAPI routes and dependency injection
│   ├── __init__.py
│   ├── dependencies.py  # DI container setup
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── lists.py     # List CRUD endpoints
│   │   ├── urls.py      # URL management endpoints
│   │   └── public.py    # Public slug access
│   └── schemas/         # Pydantic request/response models
│       ├── __init__.py
│       ├── list_schemas.py
│       └── url_schemas.py
├── domain/              # Business logic and services
│   ├── __init__.py
│   ├── models.py        # Domain entities (not ORM models)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── list_service.py
│   │   └── url_service.py
│   └── exceptions.py    # Domain-specific exceptions
├── infrastructure/      # Data access and external concerns
│   ├── __init__.py
│   ├── database.py      # SQLAlchemy setup and session management
│   ├── models.py        # SQLAlchemy ORM models
│   └── repositories/
│       ├── __init__.py
│       ├── base.py      # Base repository interface
│       ├── list_repository.py
│       └── url_repository.py
├── core/                # Configuration and utilities
│   ├── __init__.py
│   ├── config.py        # Settings (Pydantic BaseSettings)
│   └── logging.py       # Structured logging setup
└── main.py              # Application entry point

tests/
├── conftest.py          # Pytest fixtures (test DB, client)
├── contract/            # API contract tests (OpenAPI compliance)
│   ├── __init__.py
│   └── test_api_contracts.py
├── integration/         # End-to-end API tests
│   ├── __init__.py
│   ├── test_list_workflows.py
│   ├── test_url_workflows.py
│   └── test_public_access.py
└── unit/                # Isolated component tests
    ├── __init__.py
    ├── services/
    │   ├── test_list_service.py
    │   └── test_url_service.py
    └── repositories/
        ├── test_list_repository.py
        └── test_url_repository.py

alembic/                 # Database migrations
├── versions/
└── env.py

Root files:
├── pyproject.toml       # Poetry/pip dependencies, tool configs
├── pytest.ini           # Pytest configuration
├── .gitignore
└── README.md            # Generated from quickstart.md
```

**Structure Decision**: Single project backend API structure selected. No frontend components (API-only). Three-layer architecture (API/Domain/Infrastructure) chosen to support Repository pattern and Service layer as specified by user. Test structure mirrors source with contract/integration/unit separation per constitution's testing principles.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Repository Pattern (optional) | User explicitly requested. Data access patterns complex: by-ID, by-slug, by-status queries; cascade deletes; slug uniqueness checks across transactions. Enables testing without database, clean PostgreSQL migration. | Direct SQLAlchemy in services → Tight coupling to ORM prevents testing business logic without DB; makes future storage changes (PostgreSQL, caching layer) require rewriting service layer; violates dependency inversion; creates hard-to-test service methods. Repository abstraction warranted by 6+ distinct query patterns and testing requirements. |
| Service Layer (Clean Arch aspect) | User requested Service Layer + DI. Business rules complex: state transitions (draft↔published), slug uniqueness enforcement, cascade delete coordination, validation orchestration. Services encapsulate multi-step operations and transaction boundaries. | Fat controllers with inline logic → Mixes HTTP concerns with business rules; cannot test validation/state transitions without HTTP layer; duplicates logic across endpoints; 404 vs 400 error mapping scattered; slug collision handling repeated. Service layer justified by 10+ business rules requiring isolation and reuse. |
