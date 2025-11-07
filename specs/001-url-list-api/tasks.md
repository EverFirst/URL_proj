# Tasks: URL List Management API

**Input**: Design documents from `/specs/001-url-list-api/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/openapi.yaml

**Tests**: Tests are REQUIRED per FR-038/039 and constitution (70% coverage minimum, TDD recommended)

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project directory structure: `src/api/`, `src/domain/`, `src/infrastructure/`, `src/core/`, `tests/`, `alembic/`
- [ ] T002 Initialize Python project with `pyproject.toml` (Poetry) or `requirements.txt` including FastAPI 0.104+, SQLAlchemy 2.0+, Pydantic v2, Alembic, pytest, httpx, pytest-cov
- [ ] T003 [P] Create `.gitignore` for Python (exclude `__pycache__/`, `*.db`, `.env`, `htmlcov/`, `.pytest_cache/`)
- [ ] T004 [P] Create `.env` template with `DATABASE_URL`, `API_HOST`, `API_PORT`, `LOG_LEVEL`
- [ ] T005 [P] Create `pytest.ini` with coverage config (fail_under=70, testpaths=tests, asyncio_mode=auto)
- [ ] T006 [P] Create all `__init__.py` files in src/ and tests/ directories
- [ ] T007 Initialize Alembic with `alembic init alembic` and configure `alembic.ini` for SQLite

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Implement configuration management in `src/core/config.py` using Pydantic BaseSettings
- [ ] T009 [P] Implement structured logging setup in `src/core/logging.py` with JSON formatter and request context
- [ ] T010 Implement database session management in `src/infrastructure/database.py` (SQLAlchemy engine, sessionmaker, get_db dependency)
- [ ] T011 Create SQLAlchemy Base and ORM models in `src/infrastructure/models.py` (URLListModel with id, title, slug, status, timestamps; URLItemModel with id, list_id, url, title, created_at; relationships and cascade)
- [ ] T012 Create base repository interface in `src/infrastructure/repositories/base.py` (Generic[T] with get_by_id, get_all, create, update, delete abstract methods)
- [ ] T013 Create domain exceptions in `src/domain/exceptions.py` (NotFoundError, ValidationError, ConflictError)
- [ ] T014 Configure FastAPI app in `src/main.py` (app instance, CORS, exception handlers for domain exceptions, logging middleware, OpenAPI config)
- [ ] T015 Implement dependency injection setup in `src/api/dependencies.py` (get_db, repository factories, service factories)
- [ ] T016 Create pytest fixtures in `tests/conftest.py` (test_db with in-memory SQLite, test_client with httpx.AsyncClient, mock repositories)
- [ ] T017 Generate initial Alembic migration for URLListModel and URLItemModel tables with indexes
- [ ] T018 Apply initial migration and verify database schema creation

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create and Manage URL Lists (Priority: P1) 🎯 MVP

**Goal**: Enable CRUD operations on URL lists - users can create, view, update, and delete lists

**Independent Test**: Create a list via API, retrieve it by ID, update its title, delete it, verify 404 on subsequent retrieval. Verify data persists across system restarts.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T019 [P] [US1] Write contract test for POST /lists in `tests/contract/test_list_contracts.py` (verify 201 response schema matches OpenAPI spec)
- [ ] T020 [P] [US1] Write contract test for GET /lists in `tests/contract/test_list_contracts.py` (verify 200 response array schema)
- [ ] T021 [P] [US1] Write contract test for GET /lists/{id} in `tests/contract/test_list_contracts.py` (verify 200 and 404 response schemas)
- [ ] T022 [P] [US1] Write contract test for PATCH /lists/{id} in `tests/contract/test_list_contracts.py` (verify 200, 400, 404, 409, 422 response schemas)
- [ ] T023 [P] [US1] Write contract test for DELETE /lists/{id} in `tests/contract/test_list_contracts.py` (verify 204 and 404 responses)
- [ ] T024 [P] [US1] Write integration test for create list workflow in `tests/integration/test_list_workflows.py` (Acceptance Scenario #1)
- [ ] T025 [P] [US1] Write integration test for retrieve list workflow in `tests/integration/test_list_workflows.py` (Acceptance Scenario #2)
- [ ] T026 [P] [US1] Write integration test for update list workflow in `tests/integration/test_list_workflows.py` (Acceptance Scenario #3)
- [ ] T027 [P] [US1] Write integration test for delete list workflow in `tests/integration/test_list_workflows.py` (Acceptance Scenario #4)
- [ ] T028 [P] [US1] Write integration test for get all lists workflow in `tests/integration/test_list_workflows.py` (Acceptance Scenario #5)
- [ ] T029 [P] [US1] Write integration test for edge cases in `tests/integration/test_list_workflows.py` (empty title, title too long, delete non-existent, data persistence after restart)

**Verify all tests FAIL before proceeding to implementation**

### Implementation for User Story 1

- [ ] T030 [P] [US1] Create domain entity URLList in `src/domain/models.py` (dataclass with id, title, slug, status, timestamps, is_published method)
- [ ] T031 [P] [US1] Create Pydantic request schemas in `src/api/schemas/list_schemas.py` (ListCreateRequest with title validation 1-200 chars; ListUpdateRequest with optional title/slug/status and field validators)
- [ ] T032 [P] [US1] Create Pydantic response schema ListResponse in `src/api/schemas/list_schemas.py` (id, title, slug, status, timestamps, urls array)
- [ ] T033 [US1] Implement IListRepository interface in `src/infrastructure/repositories/list_repository.py` (extends BaseRepository, adds get_by_slug, slug_exists methods)
- [ ] T034 [US1] Implement SQLAlchemyListRepository in `src/infrastructure/repositories/list_repository.py` (ORM→domain mapping, query by ID, query all ordered by created_at, create, update, delete, get_by_slug, slug_exists with exclude_id)
- [ ] T035 [US1] Write unit tests for ListRepository in `tests/unit/repositories/test_list_repository.py` (test all methods with test DB, verify cascade delete setup)
- [ ] T036 [US1] Implement ListService in `src/domain/services/list_service.py` (create_list with title validation, get_by_id with NotFoundError, get_all, update_list with validation, delete_list, set_slug with pattern validation and uniqueness check, set_status with enum validation)
- [ ] T037 [US1] Write unit tests for ListService in `tests/unit/services/test_list_service.py` (mock repositories, test business logic, validation, error handling)
- [ ] T038 [US1] Implement POST /lists endpoint in `src/api/routes/lists.py` (inject ListService, call create_list, return 201 with ListResponse, handle ValidationError→400)
- [ ] T039 [US1] Implement GET /lists endpoint in `src/api/routes/lists.py` (inject ListService, call get_all, return 200 with List[ListResponse])
- [ ] T040 [US1] Implement GET /lists/{id} endpoint in `src/api/routes/lists.py` (inject ListService, call get_by_id, return 200 or NotFoundError→404)
- [ ] T041 [US1] Implement PATCH /lists/{id} endpoint in `src/api/routes/lists.py` (inject ListService, validate request, call update/set_slug/set_status, handle ValidationError→400, ConflictError→409, NotFoundError→404)
- [ ] T042 [US1] Implement DELETE /lists/{id} endpoint in `src/api/routes/lists.py` (inject ListService, call delete_list, return 204 or NotFoundError→404)
- [ ] T043 [US1] Register list routes in `src/main.py` (app.include_router for lists router with /lists prefix)
- [ ] T044 [US1] Add request/response logging for list endpoints (timestamp, method, path, status code)

**Verify all User Story 1 tests PASS - Run: `pytest tests/integration/test_list_workflows.py tests/contract/test_list_contracts.py -v`**

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Users can create, view, update, and delete lists via API.

---

## Phase 4: User Story 2 - Add and Manage URLs in Lists (Priority: P2)

**Goal**: Enable adding URLs to lists and managing them - users can populate lists with actual URLs

**Independent Test**: Create a list, add 3 URLs to it, retrieve the list to verify URLs are present in creation order, delete one URL, confirm only 2 remain.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T045 [P] [US2] Write contract test for POST /lists/{id}/urls in `tests/contract/test_url_contracts.py` (verify 201 response schema, 404 if list not found, 422 for invalid URL)
- [ ] T046 [P] [US2] Write contract test for GET /lists/{id}/urls in `tests/contract/test_url_contracts.py` (verify 200 response array schema, 404 if list not found)
- [ ] T047 [P] [US2] Write contract test for DELETE /lists/{id}/urls/{url_id} in `tests/contract/test_url_contracts.py` (verify 204 and 404 responses)
- [ ] T048 [P] [US2] Write integration test for add URL workflow in `tests/integration/test_url_workflows.py` (Acceptance Scenario #1 - add URL with title)
- [ ] T049 [P] [US2] Write integration test for retrieve URLs workflow in `tests/integration/test_url_workflows.py` (Acceptance Scenario #2 - get list with URLs)
- [ ] T050 [P] [US2] Write integration test for delete URL workflow in `tests/integration/test_url_workflows.py` (Acceptance Scenario #3 - delete URL)
- [ ] T051 [P] [US2] Write integration test for duplicate URLs workflow in `tests/integration/test_url_workflows.py` (Acceptance Scenario #4 - same URL twice)
- [ ] T052 [P] [US2] Write integration test for URL without title workflow in `tests/integration/test_url_workflows.py` (Acceptance Scenario #5 - null title)
- [ ] T053 [P] [US2] Write integration test for edge cases in `tests/integration/test_url_workflows.py` (add to non-existent list→404, invalid URL format, URL too long, URL ordering by created_at)

**Verify all tests FAIL before proceeding to implementation**

### Implementation for User Story 2

- [ ] T054 [P] [US2] Create domain entity URLItem in `src/domain/models.py` (dataclass with id, list_id, url, title, created_at)
- [ ] T055 [P] [US2] Create Pydantic request schema URLCreateRequest in `src/api/schemas/url_schemas.py` (url with http/https validator and max 2048 chars, optional title max 200 chars)
- [ ] T056 [P] [US2] Create Pydantic response schema URLItemResponse in `src/api/schemas/url_schemas.py` (id, url, title nullable, created_at)
- [ ] T057 [US2] Update ListResponse schema in `src/api/schemas/list_schemas.py` to include urls: List[URLItemResponse]
- [ ] T058 [US2] Implement IURLRepository interface in `src/infrastructure/repositories/url_repository.py` (extends BaseRepository, adds get_by_list_id method)
- [ ] T059 [US2] Implement SQLAlchemyURLRepository in `src/infrastructure/repositories/url_repository.py` (ORM→domain mapping, create, delete, get_by_list_id ordered by created_at ASC)
- [ ] T060 [US2] Write unit tests for URLRepository in `tests/unit/repositories/test_url_repository.py` (test all methods with test DB, verify ordering, cascade delete behavior)
- [ ] T061 [US2] Implement URLService in `src/domain/services/url_service.py` (add_url_to_list with list existence check and URL validation, get_urls_for_list, delete_url)
- [ ] T062 [US2] Write unit tests for URLService in `tests/unit/services/test_url_service.py` (mock repositories, test business logic, validation, 404 errors)
- [ ] T063 [US2] Implement POST /lists/{id}/urls endpoint in `src/api/routes/urls.py` (inject URLService, call add_url_to_list, return 201 with URLItemResponse, handle NotFoundError→404, ValidationError→422)
- [ ] T064 [US2] Implement GET /lists/{id}/urls endpoint in `src/api/routes/urls.py` (inject URLService, call get_urls_for_list, return 200 with List[URLItemResponse], handle NotFoundError→404)
- [ ] T065 [US2] Implement DELETE /lists/{id}/urls/{url_id} endpoint in `src/api/routes/urls.py` (inject URLService, call delete_url, return 204 or NotFoundError→404)
- [ ] T066 [US2] Register URL routes in `src/main.py` (app.include_router for urls router)
- [ ] T067 [US2] Update ListRepository.get_by_id to eager load URLs using joinedload (prevent N+1 queries)
- [ ] T068 [US2] Add request/response logging for URL endpoints
- [ ] T069 [US2] Integration test: Verify cascade delete - delete list with URLs, confirm URLs also deleted

**Verify all User Story 2 tests PASS - Run: `pytest tests/integration/test_url_workflows.py tests/contract/test_url_contracts.py -v`**

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Users can create lists and populate them with URLs.

---

## Phase 5: User Story 3 - Publish Lists for Public Sharing (Priority: P3)

**Goal**: Enable public sharing via slugs - anyone with a slug can view a published list

**Independent Test**: Create a list, set slug "tech-resources", publish it, retrieve via `/public/tech-resources` to verify access without list ID. Test draft list with slug returns 404 on public endpoint.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T070 [P] [US3] Write contract test for GET /public/{slug} in `tests/contract/test_public_contracts.py` (verify 200 response schema, 404 for non-existent/draft)
- [ ] T071 [P] [US3] Write integration test for publish with slug workflow in `tests/integration/test_public_access.py` (Acceptance Scenario #1 - set slug and publish, verify public access)
- [ ] T072 [P] [US3] Write integration test for public slug access workflow in `tests/integration/test_public_access.py` (Acceptance Scenario #2 - retrieve published list by slug)
- [ ] T073 [P] [US3] Write integration test for unpublish workflow in `tests/integration/test_public_access.py` (Acceptance Scenario #3 - draft list blocks slug access)
- [ ] T074 [P] [US3] Write integration test for duplicate slug rejection in `tests/integration/test_public_access.py` (Acceptance Scenario #4 - slug uniqueness)
- [ ] T075 [P] [US3] Write integration test for slug change workflow in `tests/integration/test_public_access.py` (Acceptance Scenario #5 - old slug invalid after change)
- [ ] T076 [P] [US3] Write integration test for publish without slug in `tests/integration/test_public_access.py` (Acceptance Scenario #6 - published list without slug accessible by ID only)
- [ ] T077 [P] [US3] Write integration test for edge cases in `tests/integration/test_public_access.py` (slug validation errors, setting slug on draft list, draft list with slug blocked from public access)

**Verify all tests FAIL before proceeding to implementation**

### Implementation for User Story 3

- [ ] T078 [P] [US3] Add `is_publicly_accessible()` and `can_be_accessed_by_slug(slug)` methods to URLList domain entity in `src/domain/models.py`
- [ ] T079 [US3] Update ListService.set_slug in `src/domain/services/list_service.py` to validate slug pattern `^[a-z0-9-]{3,50}$` and check uniqueness before setting
- [ ] T080 [US3] Update ListService.set_status in `src/domain/services/list_service.py` to validate status enum (draft/published)
- [ ] T081 [US3] Add PublicService.get_published_list_by_slug in `src/domain/services/public_service.py` (new file) - fetch by slug, verify status=published, return list or NotFoundError
- [ ] T082 [US3] Write unit tests for PublicService in `tests/unit/services/test_public_service.py` (mock repository, test published access, draft list blocked, non-existent slug)
- [ ] T083 [US3] Implement GET /public/{slug} endpoint in `src/api/routes/public.py` (inject PublicService, call get_published_list_by_slug, return 200 with ListResponse or NotFoundError→404)
- [ ] T084 [US3] Register public routes in `src/main.py` (app.include_router for public router with /public prefix)
- [ ] T085 [US3] Add slug validation to PATCH /lists/{id} endpoint - reject invalid slug patterns with 422
- [ ] T086 [US3] Add request/response logging for public endpoint
- [ ] T087 [US3] Integration test: Verify performance - public slug access with 100 URLs completes in <1 second (SC-005)

**Verify all User Story 3 tests PASS - Run: `pytest tests/integration/test_public_access.py tests/contract/test_public_contracts.py -v`**

**Checkpoint**: All user stories should now be independently functional. Full workflow (create → add URLs → publish) works end-to-end.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories, quality gates, and final validation

- [ ] T088 [P] Run full test suite with coverage: `pytest --cov=src --cov-report=term-missing --cov-report=html`
- [ ] T089 [P] Verify coverage meets 70% minimum per constitution (fail_under=70 in pytest.ini)
- [ ] T090 [P] Lint all code with ruff: `ruff check src tests` and fix issues
- [ ] T091 [P] Format all code with black: `black src tests`
- [ ] T092 [P] Type check with mypy: `mypy src` (if installed)
- [ ] T093 [P] Create README.md from quickstart.md with setup instructions, dev server commands, testing commands
- [ ] T094 [P] Add API usage examples to README.md (curl commands for create list → add URL → publish workflow)
- [ ] T095 Manual validation: Test all endpoints via http://localhost:8000/docs (Swagger UI) per FR-039
- [ ] T096 Manual validation: Complete full workflow in under 5 minutes via API docs (SC-001)
- [ ] T097 Manual validation: Verify data persists after server restart (SC-004) - stop uvicorn, restart, check data intact
- [ ] T098 Edge case validation: Test all validation error scenarios documented in Edge Cases section of spec.md
- [ ] T099 Performance validation: Verify P95 response times <500ms for typical operations (SC-002, use httpx to measure)
- [ ] T100 Security review: Verify no sensitive data in logs, proper error messages without stack traces in production mode
- [ ] T101 Document deployment considerations in README.md (PostgreSQL migration, environment variables, gunicorn for production)
- [ ] T102 [P] Add OpenAPI spec export test: verify `/openapi.json` matches `specs/001-url-list-api/contracts/openapi.yaml`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - **BLOCKS all user stories**
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order: US1 (P1) → US2 (P2) → US3 (P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - **No dependencies on other stories**
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Requires URLList entity from US1 but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Uses list management from US1 but independently testable

### Within Each User Story

- Tests (TDD) MUST be written FIRST and FAIL before implementation
- Models before services (services depend on domain entities)
- Services before endpoints (endpoints inject services)
- Repository tests before service tests (services depend on repositories)
- Core implementation before integration tests pass
- Story complete before moving to next priority

### Parallel Opportunities

**Setup Phase (Phase 1)**:
- T003 (gitignore), T004 (env), T005 (pytest.ini), T006 (__init__ files) can all run in parallel

**Foundational Phase (Phase 2)**:
- T008 (config) and T009 (logging) can run in parallel
- After T011 (ORM models), T012 (base repository) and T013 (exceptions) can run in parallel

**User Story 1 Tests (TDD Phase)**:
- T019-T023 (all contract tests) can run in parallel - different test files/endpoints
- T024-T029 (all integration tests) can run in parallel - different workflows

**User Story 1 Implementation**:
- T030 (domain entity), T031 (request schemas), T032 (response schema) can run in parallel - different concerns
- After repository/service complete, all endpoints T038-T042 can be implemented in parallel by different developers

**User Story 2 Tests (TDD Phase)**:
- T045-T047 (contract tests) can run in parallel
- T048-T053 (integration tests) can run in parallel

**User Story 2 Implementation**:
- T054 (domain entity), T055 (request schema), T056 (response schema) can run in parallel
- T063-T065 (all endpoints) can run in parallel

**User Story 3 Tests (TDD Phase)**:
- T070 (contract test) standalone
- T071-T077 (integration tests) can run in parallel

**User Story 3 Implementation**:
- T078 (domain methods) and T079-T080 (service updates) can run after each other but T078 is a prereq

**Polish Phase (Phase 6)**:
- T088-T094, T102 can all run in parallel - different validation/documentation tasks

**Between User Stories**:
- Once Foundational (Phase 2) completes, US1, US2, US3 can all start in parallel if team has capacity
- Each story is independently testable and deliverable

---

## Parallel Example: User Story 1

```bash
# TDD Phase - Launch all contract tests together:
Task T019: "Contract test for POST /lists in tests/contract/test_list_contracts.py"
Task T020: "Contract test for GET /lists in tests/contract/test_list_contracts.py"
Task T021: "Contract test for GET /lists/{id} in tests/contract/test_list_contracts.py"
Task T022: "Contract test for PATCH /lists/{id} in tests/contract/test_list_contracts.py"
Task T023: "Contract test for DELETE /lists/{id} in tests/contract/test_list_contracts.py"

# Then launch all integration tests together:
Task T024-T029: All integration test workflows in tests/integration/test_list_workflows.py

# Implementation Phase - Launch all schema definitions together:
Task T030: "Create domain entity URLList in src/domain/models.py"
Task T031: "Create Pydantic request schemas in src/api/schemas/list_schemas.py"
Task T032: "Create Pydantic response schema ListResponse in src/api/schemas/list_schemas.py"

# After repository and service complete, launch all endpoints together:
Task T038: "Implement POST /lists endpoint in src/api/routes/lists.py"
Task T039: "Implement GET /lists endpoint in src/api/routes/lists.py"
Task T040: "Implement GET /lists/{id} endpoint in src/api/routes/lists.py"
Task T041: "Implement PATCH /lists/{id} endpoint in src/api/routes/lists.py"
Task T042: "Implement DELETE /lists/{id} endpoint in src/api/routes/lists.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T018) - **CRITICAL - blocks all stories**
3. Complete Phase 3: User Story 1 (T019-T044)
4. **STOP and VALIDATE**: Run `pytest tests/integration/test_list_workflows.py tests/contract/test_list_contracts.py -v --cov=src`
5. Manual test via http://localhost:8000/docs
6. Deploy/demo if ready - **Users can manage lists**

### Incremental Delivery

1. Complete Setup + Foundational (T001-T018) → Foundation ready
2. Add User Story 1 (T019-T044) → Test independently → Deploy/Demo (**MVP!** - List management works)
3. Add User Story 2 (T045-T069) → Test independently → Deploy/Demo (Users can add URLs to lists)
4. Add User Story 3 (T070-T087) → Test independently → Deploy/Demo (Public sharing works)
5. Polish (T088-T102) → Final quality gates → Production ready
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (T001-T018)
2. **Once Foundational is done**:
   - **Developer A**: User Story 1 (T019-T044) - List CRUD
   - **Developer B**: User Story 2 (T045-T069) - URL management
   - **Developer C**: User Story 3 (T070-T087) - Public sharing
3. **Stories complete and integrate independently**
4. **Team reunites for Polish** (T088-T102)

---

## Notes

- **[P] tasks** = different files, no dependencies, safe for parallel execution
- **[Story] label** maps task to specific user story for traceability
- **Each user story is independently completable and testable** - can ship incrementally
- **TDD Required**: Constitution mandates 70% coverage, tests required per FR-038/039
- **Verify tests fail before implementing** - confirms tests are actually testing something
- **Commit after each task or logical group** with conventional commit format (feat/fix/test/refactor)
- **Stop at any checkpoint to validate story independently** - each story is potentially shippable
- **Type hints required on all functions** per constitution
- **All inputs validated via Pydantic** - no unvalidated data reaches business logic
- **Error handling**: 404 (not found), 400 (business rule), 422 (format), 409 (conflict), 500 (unexpected)
- **Logging**: All endpoints must log timestamp, method, path, status per constitution
- **Performance**: Aim for <500ms P95 response times per SC-002
- **Avoid**: Vague tasks, same-file conflicts, cross-story dependencies that break independence
