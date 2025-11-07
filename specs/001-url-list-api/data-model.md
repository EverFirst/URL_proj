# Data Model: URL List Management API

**Date**: 2025-11-07
**Feature**: URL List Management API
**Purpose**: Entity definitions, relationships, validation rules, and state transitions

## Entity Overview

This system manages two primary entities with a one-to-many relationship:

```
URLList (1) ────< (many) URLItem
```

## Entities

### URLList

Represents a collection of URLs that can be managed privately (draft) or shared publicly (published).

**Attributes**:

| Field | Type | Constraints | Description | Spec Reference |
|-------|------|-------------|-------------|----------------|
| id | Integer | PK, Auto-increment, NOT NULL | Unique identifier | FR-002 |
| title | String(200) | NOT NULL, 1-200 chars | Required list name | FR-001, FR-033, FR-034 |
| slug | String(50) | UNIQUE, NULL allowed, 3-50 chars, pattern: `^[a-z0-9-]+$` | Optional unique URL-safe identifier for public access | FR-030, FR-031, FR-032 |
| status | Enum("draft", "published") | NOT NULL, default="draft" | Publication status | FR-022, FR-023 |
| created_at | DateTime | NOT NULL, default=NOW() | Creation timestamp | Spec: Key Entities |
| updated_at | DateTime | NOT NULL, default=NOW(), auto-update | Last modification timestamp | Spec: Key Entities |

**Relationships**:
- **urls**: One-to-Many relationship with URLItem
  - Cascade delete: When URLList is deleted, all associated URLItems are also deleted (FR-009)
  - Ordering: URLs ordered by `created_at ASC` (FR-014 - creation order)

**Indexes**:
- Primary: `id`
- Unique: `slug` (for fast slug lookups and uniqueness enforcement - FR-032)
- Index: `status` (for filtering published lists)

**Validation Rules**:

1. **Title Validation** (FR-033, FR-034):
   - MUST NOT be empty or NULL
   - MUST be 1-200 characters
   - Enforced at: Pydantic schema, Service layer, Database constraint

2. **Slug Validation** (FR-030, FR-031):
   - If provided, MUST be 3-50 characters
   - MUST match pattern: `^[a-z0-9-]+$` (lowercase alphanumeric and hyphens only)
   - MUST be unique across all lists (even if NULL for some lists)
   - CAN be NULL (lists can exist without slugs)
   - Enforced at: Pydantic field validator, Service layer, Database unique constraint

3. **Status Validation** (FR-023):
   - MUST be exactly one of: "draft" or "published"
   - Defaults to "draft" on creation (FR-022)
   - Enforced at: Database enum, Pydantic Literal type

**State Transitions**:

```
    ┌───────┐
    │ draft │ ←─────┐
    └───┬───┘       │
        │           │
        │ publish   │ unpublish
        │           │
        ▼           │
 ┌───────────┐     │
 │ published │ ────┘
 └───────────┘
```

- **draft → published**: Allowed (FR-024)
  - Can publish without slug (FR-021 - list not accessible via slug endpoint)
  - Can publish with slug (becomes publicly accessible via slug - FR-017)
- **published → draft**: Allowed (FR-024)
  - Public slug access blocked for draft lists (FR-018)
- **Slug changes**: Allowed at any status
  - Draft list: Can set/change slug before publishing (FR-020)
  - Published list: Changing slug invalidates old slug immediately (Spec: User Story 3, Acceptance #5)

**Business Rules**:

1. **Slug Uniqueness** (FR-032):
   - No two lists can have the same slug
   - Enforced via database UNIQUE constraint
   - Service layer checks before update to provide user-friendly error

2. **Public Access Control** (FR-017, FR-018):
   - Only lists with `status='published'` AND `slug IS NOT NULL` are accessible via slug endpoint
   - Draft lists with slugs: slug reserved but not accessible
   - Published lists without slugs: accessible by ID only

3. **Cascade Delete** (FR-009):
   - Deleting a URLList deletes all associated URLItems
   - Implemented via SQLAlchemy `cascade="all, delete-orphan"`

---

### URLItem

Represents a single URL entry within a URLList.

**Attributes**:

| Field | Type | Constraints | Description | Spec Reference |
|-------|------|-------------|-------------|----------------|
| id | Integer | PK, Auto-increment, NOT NULL | Unique identifier | FR-012 |
| list_id | Integer | FK(url_lists.id), NOT NULL, Indexed | Parent list reference | FR-010 |
| url | String(2048) | NOT NULL, max 2048 chars, pattern: `^https?://` | The actual URL | FR-028, FR-029 |
| title | String(200) | NULL allowed, max 200 chars | Optional descriptive title | FR-011 |
| created_at | DateTime | NOT NULL, default=NOW() | Creation timestamp (for ordering) | FR-014 |

**Relationships**:
- **list**: Many-to-One relationship with URLList
  - Foreign key constraint to `url_lists.id`
  - ON DELETE CASCADE (enforced at database level)

**Indexes**:
- Primary: `id`
- Foreign Key Index: `list_id` (for efficient joins and filtering)
- Index: `created_at` (for ordering URLs within a list - FR-014)

**Validation Rules**:

1. **URL Validation** (FR-028, FR-029):
   - MUST NOT be NULL
   - MUST start with `http://` or `https://`
   - MUST be ≤2048 characters
   - Enforced at: Pydantic field validator, Service layer

2. **Title Validation** (FR-011):
   - CAN be NULL (optional)
   - If provided, MUST be ≤200 characters
   - Enforced at: Pydantic schema (Optional[str]), Database constraint

3. **List Association** (FR-010):
   - MUST reference an existing URLList (foreign key constraint)
   - Service layer validates list existence before creating URL (returns 404 if list not found - FR-036)

**Business Rules**:

1. **Duplicate URLs Allowed** (FR-016):
   - Same URL can appear multiple times in the same list
   - Each instance gets unique `id`
   - No uniqueness constraint on `url` field

2. **Ordering** (FR-014):
   - URLs within a list returned in creation order (first added appears first)
   - Implemented via `ORDER BY created_at ASC` in repository queries

3. **Orphan Prevention** (FR-009):
   - Cannot exist without parent URLList
   - Automatically deleted when parent list is deleted
   - Foreign key constraint prevents orphaned URL items

---

## Relationships Diagram

```
┌────────────────────────────────────┐
│ URLList                            │
├────────────────────────────────────┤
│ id (PK)                            │
│ title (NOT NULL, 1-200 chars)     │
│ slug (UNIQUE, NULL ok, 3-50 chars)│
│ status (ENUM: draft/published)    │
│ created_at (DateTime)              │
│ updated_at (DateTime)              │
└───────────┬────────────────────────┘
            │
            │ 1:N (cascade delete)
            │
            ▼
┌────────────────────────────────────┐
│ URLItem                            │
├────────────────────────────────────┤
│ id (PK)                            │
│ list_id (FK → URLList.id)          │
│ url (NOT NULL, ≤2048 chars)       │
│ title (NULL ok, ≤200 chars)       │
│ created_at (DateTime)              │
└────────────────────────────────────┘
```

## Database Schema (SQLAlchemy)

```sql
-- Generated by Alembic migration

CREATE TABLE url_lists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL CHECK(length(title) >= 1 AND length(title) <= 200),
    slug VARCHAR(50) UNIQUE CHECK(slug IS NULL OR (length(slug) >= 3 AND length(slug) <= 50)),
    status VARCHAR(20) NOT NULL DEFAULT 'draft' CHECK(status IN ('draft', 'published')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_url_lists_slug ON url_lists (slug);
CREATE INDEX ix_url_lists_status ON url_lists (status);

CREATE TABLE url_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    list_id INTEGER NOT NULL REFERENCES url_lists(id) ON DELETE CASCADE,
    url VARCHAR(2048) NOT NULL CHECK(length(url) <= 2048),
    title VARCHAR(200) CHECK(title IS NULL OR length(title) <= 200),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_url_items_list_id ON url_items (list_id);
CREATE INDEX ix_url_items_created_at ON url_items (created_at);
```

## Domain Models (Python)

### URLList Domain Entity

```python
# domain/models.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Literal

@dataclass
class URLList:
    id: Optional[int]  # None for new entities
    title: str
    slug: Optional[str]
    status: Literal["draft", "published"]
    created_at: datetime
    updated_at: datetime
    urls: List['URLItem'] = field(default_factory=list)

    def is_published(self) -> bool:
        return self.status == "published"

    def is_publicly_accessible(self) -> bool:
        """Returns True if list is accessible via slug endpoint"""
        return self.status == "published" and self.slug is not None

    def can_be_accessed_by_slug(self, requested_slug: str) -> bool:
        """Business rule: only published lists with matching slug are accessible"""
        return self.is_publicly_accessible() and self.slug == requested_slug
```

### URLItem Domain Entity

```python
@dataclass
class URLItem:
    id: Optional[int]
    list_id: int
    url: str
    title: Optional[str]
    created_at: datetime
```

## Validation Summary

| Rule | Entity | Field | Enforcement Layers | Error Response |
|------|--------|-------|-------------------|----------------|
| Title required | URLList | title | Pydantic, Service, DB NOT NULL | 400 Bad Request |
| Title 1-200 chars | URLList | title | Pydantic Field, DB CHECK | 422 Unprocessable Entity |
| Slug pattern | URLList | slug | Pydantic validator, Service regex | 422 Unprocessable Entity |
| Slug 3-50 chars | URLList | slug | Pydantic Field, DB CHECK | 422 Unprocessable Entity |
| Slug unique | URLList | slug | Service check, DB UNIQUE | 409 Conflict |
| Status enum | URLList | status | Pydantic Literal, DB CHECK | 422 Unprocessable Entity |
| URL starts http(s) | URLItem | url | Pydantic validator, Service | 422 Unprocessable Entity |
| URL ≤2048 chars | URLItem | url | Pydantic Field, DB CHECK | 422 Unprocessable Entity |
| Title ≤200 chars | URLItem | title | Pydantic Field, DB CHECK | 422 Unprocessable Entity |
| List exists | URLItem | list_id | Service check, DB FK | 404 Not Found |
| Resource exists | Both | id | Service check | 404 Not Found |

## Migration Strategy

**Initial Migration** (v1):
```bash
alembic revision --autogenerate -m "Create url_lists and url_items tables"
alembic upgrade head
```

**Indexes**:
- Create indexes on `slug`, `status`, `list_id`, `created_at` for query performance

**Data Integrity**:
- Foreign key constraints enforced at database level
- Cascade delete configured via SQLAlchemy relationship
- Unique constraints prevent slug collisions
- Check constraints enforce length and enum validity

## Query Patterns

### Common Queries

1. **Get list by ID** (FR-003):
   ```sql
   SELECT * FROM url_lists WHERE id = ?
   ```

2. **Get list by slug** (FR-017):
   ```sql
   SELECT * FROM url_lists WHERE slug = ? AND status = 'published'
   ```

3. **Get all lists** (FR-004):
   ```sql
   SELECT * FROM url_lists ORDER BY created_at ASC
   ```

4. **Get URLs for list** (FR-013, FR-014):
   ```sql
   SELECT * FROM url_items WHERE list_id = ? ORDER BY created_at ASC
   ```

5. **Check slug uniqueness** (FR-032):
   ```sql
   SELECT COUNT(*) FROM url_lists WHERE slug = ? AND id != ?
   ```

6. **Delete list with URLs** (FR-009):
   ```sql
   DELETE FROM url_lists WHERE id = ?  -- CASCADE handles url_items
   ```

## Summary

Two entities (URLList, URLItem) with 1:N relationship and cascade delete. URLList supports draft/published states with optional slug-based public access. Validation enforced at three layers (Pydantic, Service, Database). All functional requirements (FR-001 through FR-039) mapped to specific fields and constraints. Ready for API contract definition (OpenAPI spec).
