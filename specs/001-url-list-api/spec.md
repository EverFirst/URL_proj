# Feature Specification: URL List Management API

**Feature Branch**: `001-url-list-api`
**Created**: 2025-11-07
**Status**: Draft
**Input**: User description: "URL List 관리 API - 리스트 생성/조회/수정/삭제, URL 추가/관리, Slug 공유, Draft/Published 상태 관리"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create and Manage URL Lists (Priority: P1)

A user wants to organize URLs into named collections for personal reference or later sharing. They create a new list with a title, add it to draft mode, and can view all their lists.

**Why this priority**: Core CRUD functionality is the foundation - without creating and managing lists, no other features can function. This represents the minimum viable product.

**Independent Test**: Can be fully tested by creating a list via API, retrieving it by ID, updating its title, and verifying changes persist across system restarts.

**Acceptance Scenarios**:

1. **Given** no lists exist, **When** user creates a list with title "My Favorite Tools", **Then** system returns the new list with a unique ID and draft status
2. **Given** a list exists with ID 123, **When** user requests list 123, **Then** system returns the list with title, slug, status, and creation timestamp
3. **Given** a list exists with title "Old Title", **When** user updates it to "New Title", **Then** subsequent retrieval shows "New Title"
4. **Given** a list exists with ID 456, **When** user deletes list 456, **Then** subsequent retrieval returns "not found" error
5. **Given** multiple lists exist, **When** user requests all lists, **Then** system returns complete collection without pagination

---

### User Story 2 - Add and Manage URLs in Lists (Priority: P2)

A user wants to populate their lists with actual URLs. They add URLs one by one to a specific list, optionally providing titles, and can remove URLs they no longer want.

**Why this priority**: Lists are useless without URLs. This is the second critical piece that makes the feature functional and valuable.

**Independent Test**: Can be tested by creating a list, adding 3 URLs to it, retrieving the list to verify URLs are present, then removing one URL and confirming only 2 remain.

**Acceptance Scenarios**:

1. **Given** a list exists with ID 123, **When** user adds URL "https://example.com" with title "Example Site", **Then** the URL appears in the list with a unique URL ID
2. **Given** a list contains URL with ID 789, **When** user requests list details, **Then** response includes all URLs with their IDs, URLs, and titles
3. **Given** a list contains URL with ID 789, **When** user deletes URL 789, **Then** subsequent list retrieval excludes that URL
4. **Given** a list exists, **When** user adds the same URL twice, **Then** both entries are created independently (duplicates allowed)
5. **Given** user adds URL without a title, **When** viewing the list, **Then** URL appears with empty/null title

---

### User Story 3 - Publish Lists for Public Sharing (Priority: P3)

A user wants to share their curated URL collection publicly. They assign a unique slug to their list, change status to "published", and anyone with the slug can view the list without authentication.

**Why this priority**: Public sharing is valuable but not essential for personal use. Users can create and manage lists privately before deciding to publish.

**Independent Test**: Can be tested by creating a list, setting slug "tech-resources", publishing it, then retrieving via the public slug endpoint to verify access without list ID.

**Acceptance Scenarios**:

1. **Given** a draft list exists, **When** user sets slug to "my-tools" and status to "published", **Then** the list becomes publicly accessible via slug
2. **Given** a published list has slug "my-tools", **When** anyone requests public URL with slug "my-tools", **Then** they receive the list with all URLs
3. **Given** a published list exists, **When** user changes status back to "draft", **Then** public slug access returns "not found" or "not published" error
4. **Given** two users try to use slug "popular", **When** second user attempts to save, **Then** system rejects with "slug already exists" error
5. **Given** a published list with slug "old-slug", **When** user changes slug to "new-slug", **Then** old slug becomes invalid and new slug works

---

### Edge Cases

- What happens when user tries to create a list with empty/missing title?
- What happens when user tries to add a URL to a non-existent list ID?
- What happens when user provides invalid URL format (not http/https)?
- What happens when URL exceeds 2048 characters?
- What happens when slug contains uppercase letters or special characters?
- What happens when slug is shorter than 3 characters or longer than 50 characters?
- What happens when title exceeds 200 characters?
- What happens when user tries to delete a non-existent list?
- What happens when user tries to access a draft list via public slug?
- What happens when user sets slug on a draft list (allowed or requires published status)?
- What happens when user tries to publish a list without setting a slug first?
- What happens when database is restarted - do lists and URLs persist?

## Requirements *(mandatory)*

### Functional Requirements

**List Management**:

- **FR-001**: System MUST allow creating a new URL list with a title
- **FR-002**: System MUST assign a unique identifier to each created list
- **FR-003**: System MUST allow retrieving a specific list by its unique identifier
- **FR-004**: System MUST allow retrieving all lists in the system
- **FR-005**: System MUST allow updating a list's title
- **FR-006**: System MUST allow updating a list's slug
- **FR-007**: System MUST allow updating a list's status (draft or published)
- **FR-008**: System MUST allow deleting a list by its identifier
- **FR-009**: System MUST delete all associated URLs when a list is deleted

**URL Management**:

- **FR-010**: System MUST allow adding a URL to a specific list
- **FR-011**: System MUST allow optionally providing a title when adding a URL
- **FR-012**: System MUST assign a unique identifier to each URL entry
- **FR-013**: System MUST allow retrieving all URLs belonging to a specific list
- **FR-014**: System MUST allow deleting a specific URL from a list by URL identifier
- **FR-015**: System MUST allow duplicate URLs within the same list (each with unique ID)

**Public Sharing**:

- **FR-016**: System MUST allow retrieving a published list by its slug
- **FR-017**: System MUST prevent slug-based access to draft lists
- **FR-018**: System MUST enforce slug uniqueness across all lists

**Status Management**:

- **FR-019**: System MUST set new lists to "draft" status by default
- **FR-020**: System MUST support exactly two status values: "draft" and "published"
- **FR-021**: System MUST allow transitioning between draft and published states

**Data Persistence**:

- **FR-022**: System MUST persist all lists and URLs to permanent storage
- **FR-023**: System MUST retain all data after application restart
- **FR-024**: System MUST maintain data integrity across create/update/delete operations

**Validation & Error Handling**:

- **FR-025**: System MUST validate that URLs start with "http://" or "https://"
- **FR-026**: System MUST reject URLs longer than 2048 characters
- **FR-027**: System MUST validate that slugs contain only lowercase letters, numbers, and hyphens
- **FR-028**: System MUST reject slugs shorter than 3 characters or longer than 50 characters
- **FR-029**: System MUST reject duplicate slugs across all lists
- **FR-030**: System MUST reject titles longer than 200 characters
- **FR-031**: System MUST return appropriate error messages for all validation failures
- **FR-032**: System MUST return appropriate error codes for not-found resources
- **FR-033**: System MUST handle malformed requests gracefully with clear error messages

**API Documentation**:

- **FR-034**: System MUST provide interactive API documentation for all endpoints
- **FR-035**: System MUST allow testing all endpoints directly from documentation interface

### Key Entities

- **URLList**: Represents a collection of URLs. Contains unique identifier, title (up to 200 characters), optional slug (3-50 characters, lowercase alphanumeric and hyphens), status (draft or published), creation timestamp, and last updated timestamp. Relationship: one list contains zero or more URLItems.

- **URLItem**: Represents a single URL entry within a list. Contains unique identifier, the URL string (http/https, max 2048 characters), optional title (up to 200 characters), creation timestamp, and reference to parent list. Relationship: many URLItems belong to one URLList.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete the full workflow (create list → add URLs → publish) in under 5 minutes using the API documentation interface
- **SC-002**: All API endpoints respond with appropriate HTTP status codes (2xx for success, 4xx for client errors, 5xx for server errors)
- **SC-003**: 100% of invalid inputs (malformed URLs, invalid slugs, excessive lengths) are rejected with clear error messages
- **SC-004**: Data persists correctly with 100% accuracy after system restart (all lists and URLs remain intact)
- **SC-005**: Public slug access returns correct list data within 1 second for lists containing up to 100 URLs
- **SC-006**: Duplicate slug attempts are rejected 100% of the time with appropriate error response
- **SC-007**: Users can successfully test all endpoints through the interactive API documentation without external tools
- **SC-008**: All CRUD operations complete successfully without data loss or corruption
- **SC-009**: Draft lists are inaccessible via slug endpoint 100% of the time (proper access control)
- **SC-010**: System handles concurrent requests to create lists with the same slug correctly (only one succeeds)

### Assumptions

- **Performance**: Standard web API response times are acceptable (under 1 second for typical operations)
- **Scale**: System will handle dozens to hundreds of lists initially (not thousands)
- **Concurrency**: Low to moderate concurrent usage expected (not high-traffic production scale)
- **Authentication**: No user authentication means all lists are accessible by ID to anyone (acceptable tradeoff stated in constraints)
- **Data Retention**: Indefinite retention is acceptable (no automatic cleanup or archival needed)
- **URL Validation**: Basic protocol and length validation is sufficient (no DNS lookup, reachability check, or content verification needed)
- **Ordering**: Lists and URLs returned in creation order or database natural order (no specific sorting requirements)
- **Metadata**: No automatic URL metadata extraction (title, description, favicon) as explicitly excluded in constraints
- **Search**: No search or filtering capabilities needed as explicitly excluded in constraints
- **Pagination**: Full retrieval of all lists/URLs is acceptable without pagination as explicitly excluded in constraints
