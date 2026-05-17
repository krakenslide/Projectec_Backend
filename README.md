# Production-Grade Project Management Tool — System Design

> **Target:** YouTrack/Linear-grade SaaS product  
> **Stack:** FastAPI · React/TypeScript/Tailwind · PostgreSQL · Redis · S3  
> **Author note:** This is an opinionated, implementation-ready blueprint. Every choice is justified with tradeoffs.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Database Design](#2-database-design)
3. [Backend APIs](#3-backend-apis)
4. [Frontend Structure](#4-frontend-structure)
5. [AI Agent Design](#5-ai-agent-design)
6. [Plugin System](#6-plugin-system)
7. [Authentication System](#7-authentication-system)
8. [DevOps & Deployment](#8-devops--deployment)
9. [MVP Plan & Roadmap](#9-mvp-plan--roadmap)
10. [Scaling Plan](#10-scaling-plan)
11. [Risks & Tradeoffs](#11-risks--tradeoffs)

---

## 1. Architecture Overview

### 1.1 Service Architecture Decision: Modular Monolith → Selective Microservices

**Do NOT start with microservices.** This is a startup product. Start with a **modular monolith**, then extract services only when data proves you need to.

```
┌─────────────────────────────────────────────────────────────┐
│                        API Gateway (Nginx / Traefik)         │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────▼──────────────┐
         │     FastAPI Monolith        │
         │  ┌────────┐  ┌──────────┐  │
         │  │ Auth   │  │ Projects │  │
         │  │ Module │  │ Module   │  │
         │  ├────────┤  ├──────────┤  │
         │  │ Issues │  │ Boards   │  │
         │  │ Module │  │ Module   │  │
         │  ├────────┤  ├──────────┤  │
         │  │  Docs  │  │ Search   │  │
         │  │ Module │  │ Module   │  │
         │  ├────────┤  ├──────────┤  │
         │  │  AI    │  │ Plugin   │  │
         │  │ Module │  │ Registry │  │
         │  └────────┘  └──────────┘  │
         └──────┬──────────────┬──────┘
                │              │
    ┌───────────▼──┐    ┌──────▼──────────┐
    │  PostgreSQL  │    │  Redis           │
    │  (primary)   │    │  (cache/queues)  │
    └──────────────┘    └─────────────────┘
         │
    ┌────▼──────────┐   ┌─────────────────┐
    │  S3/MinIO     │   │  Celery Workers  │
    │  (attachments)│   │  (background     │
    └───────────────┘   │   jobs)          │
                        └─────────────────┘
```

**Why modular monolith over microservices at start:**
- Teams < 10 engineers cannot operate 10 services reliably
- Shared DB transactions are possible (critical for data consistency)
- No network latency between modules
- Single deployment unit = simpler CI/CD
- **Exit strategy exists**: each module has a clean boundary (own router, service layer, DB models) — can be extracted later

**Microservices to extract in Phase 3+:**
- AI Agent service (resource-intensive, needs independent scaling)
- Notification service (high I/O, independently scalable)
- Search indexer (Elasticsearch/OpenSearch worker)

---

### 1.2 API Design: REST with selective GraphQL

**Decision: REST for CRUD operations, optional GraphQL for complex queries (board views, dashboards)**

**Why not full GraphQL:**
- N+1 problem requires DataLoader — adds complexity
- REST caching is simpler (HTTP cache headers, CDN)
- OpenAPI/Swagger docs are free with FastAPI
- Most CRUD operations don't need field selection

**Why REST wins here:**
- FastAPI generates OpenAPI 3.0 automatically
- Easier to build public API and webhooks on REST
- Standard HTTP semantics (GET is cacheable, POST is not)

**GraphQL added only for:**
- Board view (complex nested queries: sprint → stories → issues → assignees)
- Dashboard aggregations (avoid 10+ REST calls)

---

### 1.3 Issue Hierarchy — Validation & Improvement

**Your proposed hierarchy:**
```
Project → Milestone → Story → Issue → Subtask + Linked Issues
```

**Problems with this:**

1. **5 levels is too deep for most teams** — cognitive overhead is real
2. **Milestone is time-based, not structural** — mixing calendar with hierarchy
3. **"Issue" and "Story" overlap** — Story IS an issue with type=Story

**Recommended hierarchy:**

```
Organization
  └── Project (workspace boundary)
        └── Epic (large feature bucket, optional)
              └── Story / Issue / Task / Bug  (same table, type field)
                    └── Subtask (max 1 level, same table, parent_id)
```

**Cross-cutting:**
- **Sprint** is NOT part of hierarchy — it's a time-box container
- **Milestone** is a label/tag on an issue set, not a parent
- **Linked Issues**: separate `issue_links` table with relationship type (blocks, duplicates, relates-to)

**Why this is better:**
- All work items in ONE table (`issues`) with `type` enum — massive simplification
- `parent_id` for subtasks (self-referential FK, max 1 level enforced in app logic)
- Epic is optional — small teams skip it
- Sprint assignment is M2M (`sprint_issues` table)
- Milestone is a tagged date goal, not structural

**The single-table approach (like Linear) scales better:**
- Uniform API surface: everything is `GET /issues/:id`
- Consistent filtering, search, and permissions
- No JOIN tree hell

---

## 2. Database Design

### 2.1 Primary Database: PostgreSQL 16

**Why PostgreSQL over alternatives:**

| Criterion | PostgreSQL | MongoDB | MySQL |
|-----------|-----------|---------|-------|
| ACID transactions | ✅ Full | ⚠️ Limited | ✅ Full |
| JSON/JSONB support | ✅ Excellent | ✅ Native | ⚠️ Basic |
| Full-text search | ✅ Built-in | ✅ Good | ⚠️ Limited |
| Custom fields (dynamic schema) | ✅ JSONB | ✅ Native | ❌ Poor |
| Audit log (row versioning) | ✅ via pgaudit | ⚠️ Manual | ⚠️ Manual |
| Array columns | ✅ Native | ✅ | ❌ |
| RLS (Row-Level Security) | ✅ Native | ❌ | ❌ |
| Mature ecosystem | ✅ | ✅ | ✅ |

**PostgreSQL wins for us because:**
- Custom fields can live in `JSONB` column (schema-less flexibility + indexable)
- `pg_trgm` for fuzzy text search (avoid Elasticsearch for Phase 1)
- `LISTEN/NOTIFY` for real-time events
- Row Level Security for multi-tenancy (defense in depth)
- Excellent support in SQLAlchemy/Alembic

**Supporting stores:**
- **Redis 7**: Sessions, rate limiting, Celery broker, real-time pub/sub
- **S3/MinIO**: File attachments (never store BLOBs in Postgres)
- **pgvector** (extension): Vector embeddings for AI/RAG (stays in same Postgres instance)

---

### 2.2 Multi-tenancy Strategy: Schema-per-Tenant vs Row-Level

**Decision: Row-Level Isolation with `org_id` + PostgreSQL RLS**

**Why not schema-per-tenant:**
- Schema-per-tenant: Alembic migrations must run N times (one per tenant) — operational nightmare at 1000+ tenants
- Connection pooling breaks (PgBouncer can't share pools across schemas efficiently)

**Row-level isolation with RLS:**
- Single schema, every table has `org_id UUID NOT NULL`
- PostgreSQL RLS policies enforce `org_id = current_setting('app.org_id')`
- Application layer sets `SET LOCAL app.org_id = 'xxx'` at query start
- Even if app has a bug and forgets a WHERE clause, DB rejects cross-tenant reads

```sql
-- Example RLS policy
ALTER TABLE issues ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON issues
  USING (org_id = current_setting('app.org_id')::uuid);
```

---

### 2.3 Core Schema

```sql
-- =====================
-- ORGANIZATIONS / AUTH
-- =====================

CREATE TABLE organizations (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug          TEXT UNIQUE NOT NULL,  -- used in URLs: app.io/acme/
  name          TEXT NOT NULL,
  plan          TEXT NOT NULL DEFAULT 'free', -- free|pro|enterprise
  settings      JSONB DEFAULT '{}',    -- feature flags, AI config, etc.
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE users (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email         TEXT UNIQUE NOT NULL,
  display_name  TEXT NOT NULL,
  avatar_url    TEXT,
  password_hash TEXT,                  -- NULL if SSO-only
  auth_provider TEXT,                  -- 'local'|'google'|'ldap'|'saml'
  external_id   TEXT,                  -- provider's user ID
  is_active     BOOLEAN DEFAULT TRUE,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE org_memberships (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id        UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role          TEXT NOT NULL DEFAULT 'member', -- owner|admin|member|viewer
  joined_at     TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(org_id, user_id)
);

CREATE TABLE sessions (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash    TEXT UNIQUE NOT NULL,  -- SHA256 of opaque token
  expires_at    TIMESTAMPTZ NOT NULL,
  ip_address    INET,
  user_agent    TEXT,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- =====================
-- PROJECTS
-- =====================

CREATE TABLE projects (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id        UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  key           TEXT NOT NULL,         -- short key like 'PROJ', 'API'
  name          TEXT NOT NULL,
  description   TEXT,
  status        TEXT DEFAULT 'active', -- active|archived
  settings      JSONB DEFAULT '{}',    -- workflow config, default fields
  lead_id       UUID REFERENCES users(id),
  created_by    UUID REFERENCES users(id),
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(org_id, key)
);

-- Project-level role overrides
CREATE TABLE project_members (
  project_id    UUID REFERENCES projects(id) ON DELETE CASCADE,
  user_id       UUID REFERENCES users(id) ON DELETE CASCADE,
  role          TEXT NOT NULL DEFAULT 'member',
  PRIMARY KEY(project_id, user_id)
);

-- =====================
-- ISSUES (Universal Work Item)
-- =====================

CREATE TYPE issue_type AS ENUM ('epic', 'story', 'task', 'bug', 'subtask');
CREATE TYPE issue_priority AS ENUM ('critical', 'high', 'medium', 'low', 'none');
CREATE TYPE issue_status_category AS ENUM ('todo', 'in_progress', 'done', 'cancelled');

CREATE TABLE issue_statuses (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id    UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  name          TEXT NOT NULL,
  category      issue_status_category NOT NULL,
  color         TEXT,
  position      INT NOT NULL DEFAULT 0,
  is_default    BOOLEAN DEFAULT FALSE
);

CREATE TABLE issues (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id        UUID NOT NULL,         -- denormalized for RLS + sharding
  project_id    UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  parent_id     UUID REFERENCES issues(id) ON DELETE SET NULL, -- subtask parent
  epic_id       UUID REFERENCES issues(id) ON DELETE SET NULL, -- epic link

  -- Identity
  number        INT NOT NULL,          -- project-scoped: PROJ-42
  title         TEXT NOT NULL,
  description   JSONB,                 -- ProseMirror/Tiptap JSON doc
  type          issue_type NOT NULL DEFAULT 'task',
  priority      issue_priority DEFAULT 'medium',
  status_id     UUID REFERENCES issue_statuses(id),

  -- Assignments
  assignee_id   UUID REFERENCES users(id),
  reporter_id   UUID NOT NULL REFERENCES users(id),

  -- Estimation
  story_points  NUMERIC(6,2),
  estimate_mins INT,                   -- time estimate in minutes
  spent_mins    INT DEFAULT 0,

  -- Dates
  due_date      DATE,
  started_at    TIMESTAMPTZ,
  completed_at  TIMESTAMPTZ,

  -- Custom fields
  custom_fields JSONB DEFAULT '{}',    -- {"field_id": value, ...}

  -- Labels
  label_ids     UUID[] DEFAULT '{}',

  -- Metadata
  created_by    UUID REFERENCES users(id),
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW(),
  deleted_at    TIMESTAMPTZ,           -- soft delete

  -- Project-scoped auto-increment
  UNIQUE(project_id, number)
);

-- Counter table for issue numbers (atomic increment)
CREATE TABLE issue_counters (
  project_id    UUID PRIMARY KEY REFERENCES projects(id),
  last_number   INT NOT NULL DEFAULT 0
);

-- Indexes
CREATE INDEX idx_issues_project ON issues(project_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_issues_assignee ON issues(assignee_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_issues_status ON issues(status_id);
CREATE INDEX idx_issues_created ON issues(created_at DESC);
CREATE INDEX idx_issues_custom_fields ON issues USING GIN(custom_fields);
CREATE INDEX idx_issues_labels ON issues USING GIN(label_ids);

-- Full-text search
ALTER TABLE issues ADD COLUMN fts_vector TSVECTOR
  GENERATED ALWAYS AS (
    setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(description->>'text', '')), 'B')
  ) STORED;
CREATE INDEX idx_issues_fts ON issues USING GIN(fts_vector);

-- =====================
-- ISSUE LINKS
-- =====================

CREATE TABLE issue_links (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id     UUID NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
  target_id     UUID NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
  link_type     TEXT NOT NULL,         -- 'blocks'|'is_blocked_by'|'duplicates'|'relates_to'
  created_by    UUID REFERENCES users(id),
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(source_id, target_id, link_type)
);

-- =====================
-- SPRINTS
-- =====================

CREATE TABLE sprints (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id    UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  name          TEXT NOT NULL,
  goal          TEXT,
  status        TEXT DEFAULT 'planning',  -- planning|active|completed
  start_date    DATE,
  end_date      DATE,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE sprint_issues (
  sprint_id     UUID REFERENCES sprints(id) ON DELETE CASCADE,
  issue_id      UUID REFERENCES issues(id) ON DELETE CASCADE,
  added_at      TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY(sprint_id, issue_id)
);

-- =====================
-- COMMENTS & ACTIVITY
-- =====================

CREATE TABLE comments (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  issue_id      UUID NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
  parent_id     UUID REFERENCES comments(id),  -- threaded comments
  author_id     UUID NOT NULL REFERENCES users(id),
  body          JSONB NOT NULL,         -- rich text doc
  is_internal   BOOLEAN DEFAULT FALSE,  -- internal notes (not visible to guests)
  edited_at     TIMESTAMPTZ,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  deleted_at    TIMESTAMPTZ
);

-- Immutable audit trail
CREATE TABLE activity_log (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id        UUID NOT NULL,
  entity_type   TEXT NOT NULL,         -- 'issue'|'comment'|'sprint'|'project'
  entity_id     UUID NOT NULL,
  actor_id      UUID REFERENCES users(id),
  action        TEXT NOT NULL,         -- 'created'|'updated'|'status_changed'|etc.
  old_value     JSONB,
  new_value     JSONB,
  metadata      JSONB DEFAULT '{}',    -- diff snapshot
  created_at    TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_activity_entity ON activity_log(entity_type, entity_id);
CREATE INDEX idx_activity_actor ON activity_log(actor_id, created_at DESC);

-- =====================
-- CUSTOM FIELDS
-- =====================

CREATE TYPE custom_field_type AS ENUM (
  'text', 'number', 'date', 'datetime', 'select', 'multi_select',
  'user', 'url', 'checkbox', 'duration'
);

CREATE TABLE custom_fields (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id    UUID REFERENCES projects(id) ON DELETE CASCADE,
  org_id        UUID NOT NULL,         -- NULL project_id = org-wide field
  name          TEXT NOT NULL,
  key           TEXT NOT NULL,         -- used as JSONB key in issues.custom_fields
  field_type    custom_field_type NOT NULL,
  config        JSONB DEFAULT '{}',    -- options for select, validation rules, etc.
  is_required   BOOLEAN DEFAULT FALSE,
  position      INT DEFAULT 0,
  UNIQUE(project_id, key)
);

-- =====================
-- LABELS
-- =====================

CREATE TABLE labels (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id    UUID REFERENCES projects(id) ON DELETE CASCADE,
  org_id        UUID NOT NULL,
  name          TEXT NOT NULL,
  color         TEXT NOT NULL DEFAULT '#6B7280',
  UNIQUE(project_id, name)
);

-- =====================
-- ATTACHMENTS
-- =====================

CREATE TABLE attachments (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id        UUID NOT NULL,
  entity_type   TEXT NOT NULL,         -- 'issue'|'comment'|'doc'
  entity_id     UUID NOT NULL,
  uploader_id   UUID REFERENCES users(id),
  filename      TEXT NOT NULL,
  size_bytes    BIGINT NOT NULL,
  mime_type     TEXT NOT NULL,
  storage_key   TEXT NOT NULL,         -- S3 object key
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- =====================
-- DOCUMENTATION SYSTEM
-- =====================

CREATE TABLE doc_spaces (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id    UUID REFERENCES projects(id) ON DELETE CASCADE,
  org_id        UUID NOT NULL,
  name          TEXT NOT NULL,
  slug          TEXT NOT NULL
);

CREATE TABLE docs (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  space_id      UUID NOT NULL REFERENCES doc_spaces(id) ON DELETE CASCADE,
  parent_id     UUID REFERENCES docs(id),  -- folder hierarchy
  title         TEXT NOT NULL,
  slug          TEXT NOT NULL,
  content       JSONB,                 -- ProseMirror doc
  created_by    UUID REFERENCES users(id),
  updated_by    UUID REFERENCES users(id),
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(space_id, slug)
);

-- Doc versioning (immutable snapshots)
CREATE TABLE doc_versions (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  doc_id        UUID NOT NULL REFERENCES docs(id) ON DELETE CASCADE,
  version_num   INT NOT NULL,
  content       JSONB NOT NULL,
  saved_by      UUID REFERENCES users(id),
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(doc_id, version_num)
);

-- Link issues to docs
CREATE TABLE issue_doc_links (
  issue_id      UUID REFERENCES issues(id) ON DELETE CASCADE,
  doc_id        UUID REFERENCES docs(id) ON DELETE CASCADE,
  PRIMARY KEY(issue_id, doc_id)
);

-- =====================
-- AI & VECTOR SEARCH
-- =====================

-- Requires: CREATE EXTENSION vector;
CREATE TABLE embeddings (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id        UUID NOT NULL,
  entity_type   TEXT NOT NULL,         -- 'doc'|'issue'|'comment'
  entity_id     UUID NOT NULL,
  chunk_index   INT NOT NULL DEFAULT 0,
  content_hash  TEXT NOT NULL,         -- MD5 for change detection
  embedding     vector(1536),          -- OpenAI ada-002 dims
  metadata      JSONB DEFAULT '{}',    -- title, project_id, etc.
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(entity_type, entity_id, chunk_index)
);
CREATE INDEX idx_embeddings_ivfflat ON embeddings
  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- =====================
-- NOTIFICATIONS & WEBHOOKS
-- =====================

CREATE TABLE notification_preferences (
  user_id       UUID REFERENCES users(id) ON DELETE CASCADE,
  event_type    TEXT NOT NULL,
  channel       TEXT NOT NULL,         -- 'email'|'in_app'|'slack'
  enabled       BOOLEAN DEFAULT TRUE,
  PRIMARY KEY(user_id, event_type, channel)
);

CREATE TABLE webhooks (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id        UUID NOT NULL,
  project_id    UUID,                  -- NULL = org-wide
  url           TEXT NOT NULL,
  secret        TEXT NOT NULL,         -- HMAC signing secret
  events        TEXT[] NOT NULL,       -- event types to subscribe
  is_active     BOOLEAN DEFAULT TRUE,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE webhook_deliveries (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  webhook_id    UUID REFERENCES webhooks(id) ON DELETE CASCADE,
  event_type    TEXT NOT NULL,
  payload       JSONB NOT NULL,
  status        TEXT DEFAULT 'pending', -- pending|delivered|failed
  attempts      INT DEFAULT 0,
  last_attempt  TIMESTAMPTZ,
  response_code INT,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);
```

---

### 2.4 Indexing Strategy

```sql
-- Composite indexes for common query patterns
CREATE INDEX idx_issues_project_status ON issues(project_id, status_id)
  WHERE deleted_at IS NULL;

CREATE INDEX idx_issues_assignee_project ON issues(assignee_id, project_id)
  WHERE deleted_at IS NULL;

-- Partial index for active sprints
CREATE INDEX idx_sprints_active ON sprints(project_id)
  WHERE status = 'active';

-- BRIN index for time-series activity log (append-only table)
CREATE INDEX idx_activity_time_brin ON activity_log
  USING BRIN(created_at);

-- pg_trgm for fuzzy search
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_issues_title_trgm ON issues
  USING GIN(title gin_trgm_ops);
```

---

### 2.5 Audit & Versioning

Every mutating operation writes to `activity_log` via application-layer hooks (not DB triggers — triggers are hard to test and debug).

For issue field changes, store a JSON diff:
```json
{
  "action": "updated",
  "changes": {
    "status_id": {"old": "uuid-todo", "new": "uuid-in-progress"},
    "assignee_id": {"old": null, "new": "user-uuid"}
  }
}
```

For docs, store full content snapshots in `doc_versions` (cheap with compression, invaluable for restore).

---

## 3. Backend APIs

### 3.1 Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app factory
│   ├── config.py               # Pydantic Settings
│   ├── database.py             # SQLAlchemy async engine
│   ├── dependencies.py         # Shared DI: current_user, org_ctx, db
│   ├── middleware/
│   │   ├── tenant.py           # Sets app.org_id in Postgres session
│   │   ├── logging.py          # Structured request logging
│   │   └── ratelimit.py        # Redis-backed rate limiting
│   │
│   ├── modules/
│   │   ├── auth/
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   └── providers/      # local, google, ldap, oauth
│   │   │
│   │   ├── projects/
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── models.py
│   │   │   └── schemas.py
│   │   │
│   │   ├── issues/
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── filters.py      # Complex filter parsing
│   │   │   └── search.py       # FTS + trigram search
│   │   │
│   │   ├── sprints/
│   │   ├── comments/
│   │   ├── docs/
│   │   ├── search/
│   │   ├── notifications/
│   │   └── ai/
│   │       ├── router.py
│   │       ├── agent.py        # LangChain/custom agent
│   │       ├── tools.py        # Tool definitions
│   │       ├── rag.py          # RAG retrieval
│   │       ├── embedder.py     # Embedding service
│   │       └── providers/      # openai, anthropic, ollama
│   │
│   ├── workers/
│   │   ├── celery_app.py
│   │   ├── tasks/
│   │   │   ├── email.py
│   │   │   ├── webhooks.py
│   │   │   ├── embeddings.py   # async embedding generation
│   │   │   └── reports.py
│   │
│   ├── events/
│   │   ├── bus.py              # Internal event bus
│   │   ├── handlers.py         # Route events to jobs
│   │   └── types.py            # Event type definitions
│   │
│   └── plugins/
│       ├── registry.py         # Plugin loader
│       └── base.py             # Plugin base class
│
├── alembic/                    # DB migrations
├── tests/
├── Dockerfile
└── pyproject.toml
```

---

### 3.2 Authentication Endpoints

```
POST   /api/v1/auth/register                  # email/password signup
POST   /api/v1/auth/login                     # email/password login → token
POST   /api/v1/auth/logout                    # invalidate session
POST   /api/v1/auth/refresh                   # refresh access token
GET    /api/v1/auth/me                        # current user info

# OAuth / SSO
GET    /api/v1/auth/google                    # redirect to Google OAuth
GET    /api/v1/auth/google/callback           # handle callback
POST   /api/v1/auth/ldap/login                # LDAP credential check
GET    /api/v1/auth/sso/:org_slug             # org-specific SSO entry

# Invitations
POST   /api/v1/invitations                    # invite user to org
GET    /api/v1/invitations/:token/accept      # accept invite
```

---

### 3.3 Core Resource Endpoints

```
# Organizations
GET    /api/v1/orgs/:slug
PATCH  /api/v1/orgs/:slug
GET    /api/v1/orgs/:slug/members
POST   /api/v1/orgs/:slug/members
DELETE /api/v1/orgs/:slug/members/:user_id
PATCH  /api/v1/orgs/:slug/members/:user_id   # change role

# Projects
GET    /api/v1/orgs/:slug/projects
POST   /api/v1/orgs/:slug/projects
GET    /api/v1/projects/:id
PATCH  /api/v1/projects/:id
DELETE /api/v1/projects/:id
GET    /api/v1/projects/:id/members
POST   /api/v1/projects/:id/members

# Custom Fields
GET    /api/v1/projects/:id/custom-fields
POST   /api/v1/projects/:id/custom-fields
PATCH  /api/v1/projects/:id/custom-fields/:field_id
DELETE /api/v1/projects/:id/custom-fields/:field_id

# Issue Statuses (Workflow)
GET    /api/v1/projects/:id/statuses
POST   /api/v1/projects/:id/statuses
PATCH  /api/v1/projects/:id/statuses/:status_id
DELETE /api/v1/projects/:id/statuses/:status_id
POST   /api/v1/projects/:id/statuses/reorder

# Issues
GET    /api/v1/projects/:id/issues            # filterable, paginated
POST   /api/v1/projects/:id/issues
GET    /api/v1/issues/:id                     # by UUID or PROJ-42
PATCH  /api/v1/issues/:id
DELETE /api/v1/issues/:id                     # soft delete
GET    /api/v1/issues/:id/activity
POST   /api/v1/issues/:id/links               # link to another issue
DELETE /api/v1/issues/:id/links/:link_id
POST   /api/v1/issues/:id/attachments
DELETE /api/v1/issues/:id/attachments/:att_id

# Bulk operations
POST   /api/v1/issues/bulk-update             # mass status/assign/sprint
POST   /api/v1/issues/bulk-delete

# Comments
GET    /api/v1/issues/:id/comments
POST   /api/v1/issues/:id/comments
PATCH  /api/v1/comments/:id
DELETE /api/v1/comments/:id

# Sprints
GET    /api/v1/projects/:id/sprints
POST   /api/v1/projects/:id/sprints
GET    /api/v1/sprints/:id
PATCH  /api/v1/sprints/:id
POST   /api/v1/sprints/:id/start
POST   /api/v1/sprints/:id/complete
POST   /api/v1/sprints/:id/issues            # add issues to sprint
DELETE /api/v1/sprints/:id/issues/:issue_id
GET    /api/v1/sprints/:id/burndown

# Labels
GET    /api/v1/projects/:id/labels
POST   /api/v1/projects/:id/labels
PATCH  /api/v1/projects/:id/labels/:label_id
DELETE /api/v1/projects/:id/labels/:label_id

# Search
GET    /api/v1/search?q=...&project=...&type=...    # global search
GET    /api/v1/projects/:id/search                  # project-scoped

# Documentation
GET    /api/v1/projects/:id/docs/spaces
POST   /api/v1/projects/:id/docs/spaces
GET    /api/v1/docs/spaces/:id/tree         # full doc tree
GET    /api/v1/docs/:id
POST   /api/v1/docs/:space_id               # create doc
PATCH  /api/v1/docs/:id
DELETE /api/v1/docs/:id
GET    /api/v1/docs/:id/versions
GET    /api/v1/docs/:id/versions/:version_num

# Reports & Analytics
GET    /api/v1/projects/:id/reports/burndown
GET    /api/v1/projects/:id/reports/velocity
GET    /api/v1/projects/:id/reports/cumulative-flow
GET    /api/v1/orgs/:slug/reports/workload   # per-user workload

# AI Agent
POST   /api/v1/ai/query                     # ask agent a question
POST   /api/v1/ai/action                    # agent executes an action
GET    /api/v1/ai/suggestions               # proactive suggestions
POST   /api/v1/ai/embed                     # trigger re-embedding
WebSocket /ws/ai/stream                     # streaming agent responses

# Webhooks
GET    /api/v1/orgs/:slug/webhooks
POST   /api/v1/orgs/:slug/webhooks
PATCH  /api/v1/orgs/:slug/webhooks/:id
DELETE /api/v1/orgs/:slug/webhooks/:id
GET    /api/v1/orgs/:slug/webhooks/:id/deliveries
POST   /api/v1/orgs/:slug/webhooks/:id/redeliver

# User-specific
GET    /api/v1/me/issues                    # my issues across orgs
GET    /api/v1/me/standup                   # standup data
GET    /api/v1/me/notifications
PATCH  /api/v1/me/notifications/:id/read
PATCH  /api/v1/me/notification-preferences
```

---

### 3.4 Issue Filter Query Language

Support a URL-based filter language for the issues list endpoint:

```
GET /api/v1/projects/:id/issues?
  type=bug,story
  &status=in_progress
  &assignee=me,user-uuid
  &priority=high,critical
  &sprint=current
  &label=frontend,backend
  &cf[environment]=production        # custom field
  &q=payment+gateway                 # full-text
  &sort=priority:desc,created_at:asc
  &page=1&per_page=50
```

Parse this into SQLAlchemy filters server-side. Build an AST for complex expressions later (like YouTrack's query language).

---

### 3.5 Event System

Internal event bus (synchronous dispatch, async workers consume):

```python
# app/events/types.py
@dataclass
class IssueCreatedEvent:
    issue_id: UUID
    project_id: UUID
    org_id: UUID
    actor_id: UUID

# Handlers register for event types
# On issue created:
# 1. Write to activity_log (synchronous, in same transaction)
# 2. Enqueue: send_notifications task
# 3. Enqueue: webhook_delivery task
# 4. Enqueue: update_embeddings task (if AI enabled)
```

**Why sync activity log write + async everything else:**
- Activity log must be consistent with the transaction (if issue creation fails, log shouldn't exist)
- Notifications/webhooks can tolerate eventual delivery (queue with retry)

---

### 3.6 Background Jobs (Celery)

```python
# workers/tasks/
- send_email_notification(user_id, event_type, context)
- deliver_webhook(webhook_id, event_payload)
- update_embeddings(entity_type, entity_id)       # async, runs after write
- generate_burndown_snapshot(sprint_id)            # daily cron
- send_digest_emails()                             # daily cron
- cleanup_expired_sessions()                       # hourly cron
- process_attachment_virus_scan(attachment_id)     # on upload
- generate_thumbnail(attachment_id)               # on image upload
```

**Queue configuration:**
- `default` queue: general tasks
- `high_priority` queue: webhooks, email
- `ai` queue: embedding generation (GPU-intensive, separate workers)
- `scheduled` queue: cron jobs via Celery Beat

---

## 4. Frontend Structure

### 4.1 Technology Decisions

| Concern | Choice | Why |
|---------|--------|-----|
| State management | **TanStack Query + Zustand** | React Query for server state; Zustand for UI state (board drag, modal, sidebar). Redux is overkill. |
| Routing | **React Router v6** | Feature-gated routes, nested layouts |
| Rich text | **Tiptap v2** | ProseMirror-based, extensible, good table support |
| Drag-and-drop | **@dnd-kit** | Better accessibility than react-beautiful-dnd; actively maintained |
| Forms | **React Hook Form + Zod** | Zero re-renders, runtime validation |
| Date/time | **date-fns** | Lightweight, tree-shakeable |
| Charts | **Recharts** | React-native, not a wrapper around Chart.js |
| WebSocket | **@tanstack/query + socket.io-client** | Invalidate queries on WS events |

---

### 4.2 App Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── router.tsx          # Route definitions
│   │   ├── providers.tsx       # QueryClient, auth, theme providers
│   │   └── layout/
│   │       ├── AppShell.tsx    # Sidebar + header shell
│   │       ├── Sidebar.tsx
│   │       └── CommandPalette.tsx  # Cmd+K
│   │
│   ├── features/               # Feature-based modules
│   │   ├── auth/
│   │   │   ├── pages/          # LoginPage, RegisterPage
│   │   │   ├── components/     # LoginForm, OAuthButton
│   │   │   ├── hooks/          # useAuth, useSession
│   │   │   └── api.ts          # Auth API calls
│   │   │
│   │   ├── projects/
│   │   │   ├── pages/
│   │   │   │   ├── ProjectListPage.tsx
│   │   │   │   └── ProjectSettingsPage.tsx
│   │   │   ├── components/
│   │   │   └── hooks/
│   │   │
│   │   ├── issues/
│   │   │   ├── pages/
│   │   │   │   ├── IssueListPage.tsx
│   │   │   │   └── IssueDetailPage.tsx
│   │   │   ├── components/
│   │   │   │   ├── IssueCard.tsx
│   │   │   │   ├── IssueForm.tsx
│   │   │   │   ├── IssueFilters.tsx
│   │   │   │   ├── IssueDetail/
│   │   │   │   │   ├── IssueHeader.tsx
│   │   │   │   │   ├── IssueDescription.tsx
│   │   │   │   │   ├── IssueComments.tsx
│   │   │   │   │   ├── IssueActivity.tsx
│   │   │   │   │   └── IssueSidebar.tsx
│   │   │   │   └── CustomFieldRenderer.tsx
│   │   │   └── hooks/
│   │   │       ├── useIssues.ts
│   │   │       ├── useIssueFilters.ts
│   │   │       └── useIssueUpdate.ts  # optimistic updates
│   │   │
│   │   ├── board/
│   │   │   ├── pages/
│   │   │   │   ├── KanbanBoardPage.tsx
│   │   │   │   └── ScrumBoardPage.tsx
│   │   │   ├── components/
│   │   │   │   ├── BoardColumn.tsx
│   │   │   │   ├── BoardCard.tsx
│   │   │   │   └── BoardHeader.tsx
│   │   │   └── hooks/
│   │   │       └── useBoardDnD.ts
│   │   │
│   │   ├── sprints/
│   │   │   ├── pages/
│   │   │   │   ├── SprintPlanningPage.tsx
│   │   │   │   └── SprintReviewPage.tsx
│   │   │   └── components/
│   │   │       ├── SprintBacklog.tsx
│   │   │       └── VelocityChart.tsx
│   │   │
│   │   ├── docs/
│   │   │   ├── pages/
│   │   │   │   ├── DocSpacePage.tsx
│   │   │   │   └── DocEditorPage.tsx
│   │   │   └── components/
│   │   │       ├── DocTree.tsx
│   │   │       ├── DocEditor.tsx       # Tiptap
│   │   │       └── DocVersionHistory.tsx
│   │   │
│   │   ├── reports/
│   │   │   └── pages/
│   │   │       ├── BurndownPage.tsx
│   │   │       ├── VelocityPage.tsx
│   │   │       └── WorkloadPage.tsx
│   │   │
│   │   ├── ai/
│   │   │   └── components/
│   │   │       ├── AIPanel.tsx         # sliding panel
│   │   │       ├── AIChat.tsx
│   │   │       └── AISuggestions.tsx
│   │   │
│   │   ├── standup/
│   │   │   └── pages/
│   │   │       └── StandupDashboardPage.tsx
│   │   │
│   │   └── admin/
│   │       └── pages/
│   │           ├── OrgSettingsPage.tsx
│   │           ├── MembersPage.tsx
│   │           ├── WebhooksPage.tsx
│   │           └── BillingPage.tsx
│   │
│   ├── components/             # Truly shared UI components
│   │   ├── ui/                 # Primitives (Button, Input, Modal, Badge)
│   │   ├── editor/             # Tiptap rich text editor
│   │   │   ├── Editor.tsx
│   │   │   ├── Toolbar.tsx
│   │   │   └── extensions/
│   │   ├── Avatar.tsx
│   │   ├── PriorityBadge.tsx
│   │   ├── StatusBadge.tsx
│   │   ├── UserSelect.tsx
│   │   ├── DatePicker.tsx
│   │   └── EmptyState.tsx
│   │
│   ├── hooks/                  # App-wide hooks
│   │   ├── useOrg.ts
│   │   ├── usePermissions.ts
│   │   ├── useWebSocket.ts
│   │   └── useFeatureFlag.ts
│   │
│   ├── lib/
│   │   ├── api.ts              # Axios/fetch client with auth headers
│   │   ├── queryClient.ts
│   │   └── utils.ts
│   │
│   └── types/                  # Shared TypeScript types
│       ├── issue.ts
│       ├── project.ts
│       └── user.ts
```

---

### 4.3 All Pages

| Page | Route | Key Features |
|------|-------|--------------|
| **Dashboard** | `/` | My issues, recent activity, standup prompt |
| **Standup** | `/standup` | Yesterday/Today/Blockers view |
| **Project List** | `/:org/projects` | All projects, create new |
| **Issue List** | `/:org/:proj/issues` | Filterable, sortable, groupable list |
| **Issue Detail** | `/:org/:proj/issues/:num` | Full issue view with sidebar |
| **Kanban Board** | `/:org/:proj/board` | Column-based drag-drop |
| **Sprint Board** | `/:org/:proj/board/sprint` | Scrum board with sprint selector |
| **Backlog** | `/:org/:proj/backlog` | Prioritized list, sprint assignment |
| **Sprint Planning** | `/:org/:proj/sprints/:id/plan` | Drag issues into sprint |
| **Sprint Review** | `/:org/:proj/sprints/:id/review` | Sprint summary |
| **Burndown** | `/:org/:proj/reports/burndown` | Chart + table |
| **Velocity** | `/:org/:proj/reports/velocity` | Historical velocity |
| **Workload** | `/:org/reports/workload` | Per-member issue counts |
| **Docs Home** | `/:org/:proj/docs` | Doc space tree |
| **Doc Editor** | `/:org/:proj/docs/:id` | Tiptap editor + history |
| **Org Settings** | `/:org/settings` | Name, plan, SSO config |
| **Members** | `/:org/settings/members` | Invite, role management |
| **Project Settings** | `/:org/:proj/settings` | Workflow, fields, labels |
| **Admin: Webhooks** | `/:org/settings/webhooks` | Webhook management |
| **Admin: API Keys** | `/:org/settings/api` | API key management |
| **AI Assistant** | Slide-over panel | Context-aware AI chat |

---

### 4.4 Key Component Patterns

**Optimistic Updates for Issue Status Changes:**
```typescript
const updateIssue = useMutation({
  mutationFn: (update) => api.patch(`/issues/${id}`, update),
  onMutate: async (update) => {
    await queryClient.cancelQueries(['issues', id]);
    const prev = queryClient.getQueryData(['issues', id]);
    queryClient.setQueryData(['issues', id], old => ({...old, ...update}));
    return { prev };
  },
  onError: (err, update, ctx) => {
    queryClient.setQueryData(['issues', id], ctx.prev);
    toast.error('Update failed');
  },
  onSettled: () => queryClient.invalidateQueries(['issues', id])
});
```

**Board Drag-Drop with @dnd-kit:**
```typescript
// Each column is a DroppableContainer
// Each card is a Sortable item
// onDragEnd: if column changed → call PATCH /issues/:id {status_id: newColumnId}
// Use optimistic update: move card immediately, revert on error
```

**Real-time Updates via WebSocket:**
```typescript
// Connect to WS on app load
// On issue:updated event → invalidate ['issues', id] query
// On comment:added → invalidate ['comments', issueId] query
// No need for complex socket state — just invalidate React Query cache
```

---

## 5. AI Agent Design

### 5.1 Architecture Overview

```
User Message
     │
     ▼
┌────────────────┐
│  AI Router      │  ← checks feature flag per org
│  (intent parse) │
└───────┬────────┘
        │
   ┌────▼────────────────────────────────────┐
   │              Agent Core                  │
   │  ┌─────────┐  ┌──────────┐  ┌────────┐  │
   │  │ Context  │  │ Memory   │  │ Planner│  │
   │  │ Builder  │  │ (Redis)  │  │        │  │
   │  └────┬─────┘  └────┬─────┘  └───┬───┘  │
   │       └─────────────┴────────────┘       │
   │                    │                     │
   │         ┌──────────▼───────────┐         │
   │         │    LLM Provider       │         │
   │         │  (OpenAI/Anthropic/   │         │
   │         │   Ollama/None)        │         │
   │         └──────────┬───────────┘         │
   │                    │                     │
   │              Tool Calls                  │
   └────────────────────┬─────────────────────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
   ┌─────────────┐ ┌─────────┐ ┌──────────────┐
   │ Issue Tools  │ │RAG Tool │ │ Project Tools │
   │ search_issues│ │retrieve │ │ list_projects │
   │ create_issue │ │  docs   │ │ get_sprint    │
   │ update_issue │ │         │ │ get_velocity  │
   └─────────────┘ └─────────┘ └──────────────┘
```

---

### 5.2 Provider Abstraction

```python
# app/modules/ai/providers/base.py
from abc import ABC, abstractmethod
from typing import AsyncIterator

class LLMProvider(ABC):
    @abstractmethod
    async def complete(self, messages: list[dict], tools: list[dict] = None) -> dict:
        ...
    
    @abstractmethod
    async def stream(self, messages: list[dict]) -> AsyncIterator[str]:
        ...

# app/modules/ai/providers/openai_provider.py
class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
    
    async def complete(self, messages, tools=None):
        response = await self.client.chat.completions.create(
            model=self.model, messages=messages,
            tools=tools, tool_choice="auto"
        )
        return response

# Similar for AnthropicProvider, OllamaProvider

# app/modules/ai/providers/null_provider.py
class NullProvider(LLMProvider):
    """Fallback when AI is disabled. Returns deterministic responses."""
    async def complete(self, messages, tools=None):
        return {"content": "AI is not enabled for your organization."}
```

**Provider selection per org:**
```python
def get_provider(org: Organization) -> LLMProvider:
    ai_config = org.settings.get("ai", {})
    if not ai_config.get("enabled"):
        return NullProvider()
    
    provider = ai_config.get("provider", "openai")
    match provider:
        case "openai":   return OpenAIProvider(ai_config["api_key"])
        case "anthropic": return AnthropicProvider(ai_config["api_key"])
        case "ollama":   return OllamaProvider(ai_config["base_url"])
        case _:          return NullProvider()
```

---

### 5.3 Tool Definitions

```python
AGENT_TOOLS = [
    {
        "name": "search_issues",
        "description": "Search for issues by keyword, status, assignee, sprint, or priority",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "project_id": {"type": "string"},
                "assignee": {"type": "string", "enum": ["me", "unassigned"]},
                "status": {"type": "string"},
                "sprint": {"type": "string", "enum": ["current", "next", "backlog"]},
                "limit": {"type": "integer", "default": 10}
            }
        }
    },
    {
        "name": "create_issue",
        "description": "Create a new issue or task",
        "parameters": {
            "type": "object",
            "required": ["project_id", "title"],
            "properties": {
                "project_id": {"type": "string"},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "type": {"type": "string", "enum": ["task", "bug", "story", "epic"]},
                "priority": {"type": "string"},
                "assignee_id": {"type": "string"},
                "sprint_id": {"type": "string"}
            }
        }
    },
    {
        "name": "update_issue",
        "description": "Update an existing issue's status, assignee, priority, or other fields",
        "parameters": {
            "type": "object",
            "required": ["issue_id"],
            "properties": {
                "issue_id": {"type": "string"},
                "status": {"type": "string"},
                "assignee_id": {"type": "string"},
                "priority": {"type": "string"}
            }
        }
    },
    {
        "name": "retrieve_docs",
        "description": "Search the documentation/wiki for relevant information",
        "parameters": {
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {"type": "string"},
                "project_id": {"type": "string"}
            }
        }
    },
    {
        "name": "get_sprint_status",
        "description": "Get current sprint progress, velocity, and remaining work",
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {"type": "string"},
                "sprint_id": {"type": "string"}
            }
        }
    },
    {
        "name": "get_workload",
        "description": "See how work is distributed across team members",
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {"type": "string"}
            }
        }
    }
]
```

---

### 5.4 RAG System

**Vector store: pgvector** (stays in PostgreSQL — no new infra)

For Phase 3+, if performance demands it, migrate to **Qdrant** (open-source, self-hostable).

**Chunking strategy:**
```python
# Documents: chunk by heading sections (semantic chunking)
# Issues: title + description as single chunk
# Comments: group N comments per chunk (avoid tiny chunks)

# Chunk size: 512 tokens with 50-token overlap
# Model: text-embedding-ada-002 (OpenAI) OR nomic-embed-text (local)

async def embed_doc(doc: Doc):
    chunks = semantic_chunk(doc.content, max_tokens=512, overlap=50)
    embeddings = await get_embeddings(chunks)
    # Upsert into embeddings table
    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        await db.execute("""
            INSERT INTO embeddings (org_id, entity_type, entity_id, chunk_index,
                                   content_hash, embedding, metadata)
            VALUES (:org_id, 'doc', :doc_id, :i, :hash, :emb, :meta)
            ON CONFLICT (entity_type, entity_id, chunk_index)
            DO UPDATE SET embedding = :emb, content_hash = :hash
        """, ...)
```

**RAG retrieval in agent:**
```python
async def retrieve_docs(query: str, org_id: UUID, project_id: UUID = None, k: int = 5):
    query_emb = await get_embedding(query)
    
    results = await db.fetch_all("""
        SELECT entity_type, entity_id, chunk_index, metadata,
               1 - (embedding <=> :q_emb) AS similarity
        FROM embeddings
        WHERE org_id = :org_id
          AND (:project_id IS NULL OR metadata->>'project_id' = :project_id)
        ORDER BY embedding <=> :q_emb
        LIMIT :k
    """, {"q_emb": query_emb, "org_id": org_id, "project_id": project_id, "k": k})
    
    return results  # Top-k relevant chunks
```

---

### 5.5 Safety & Permissions

```python
class AgentPermissionGuard:
    """Wraps tool execution with permission checks."""
    
    def __init__(self, current_user: User, org: Organization):
        self.user = current_user
        self.org = org
    
    async def can_execute_tool(self, tool_name: str, args: dict) -> bool:
        match tool_name:
            case "search_issues" | "get_sprint_status" | "retrieve_docs":
                return True  # Read-only, always allowed
            
            case "create_issue" | "update_issue":
                if self.user_role in ("viewer",):
                    return False
                # Verify user has access to the project
                return await self.user_has_project_access(args.get("project_id"))
            
            case _:
                return False  # Unknown tool — deny
    
    async def execute_tool(self, tool_name: str, args: dict):
        if not await self.can_execute_tool(tool_name, args):
            raise PermissionError(f"Not allowed to execute: {tool_name}")
        
        # Execute with current user as actor (audit trail)
        return await TOOL_REGISTRY[tool_name](args, actor=self.user)
```

**Prompt injection protection:**
- Never include raw user input directly in system prompt
- Sanitize tool outputs before inserting into next LLM call
- Set `max_tokens` budget per conversation turn
- Log all agent actions to `activity_log` with `actor_id = user_id`

---

### 5.6 Memory & Context

```python
class AgentContext:
    """Builds the context window for each agent call."""
    
    async def build(self, user: User, org: Organization, conversation_history: list):
        # 1. User context
        user_ctx = await self._get_user_context(user, org)
        
        # 2. Active sprint context
        sprint_ctx = await self._get_sprint_context(org)
        
        # 3. Recent activity
        activity_ctx = await self._get_recent_activity(user, limit=10)
        
        system_prompt = f"""
You are a project management assistant for {org.name}.

CURRENT USER: {user.display_name} ({user.email})
CURRENT DATE: {datetime.now().isoformat()}

USER'S ACTIVE ISSUES ({len(user_ctx['issues'])}):
{format_issues(user_ctx['issues'][:5])}

ACTIVE SPRINT: {sprint_ctx['name']} (ends {sprint_ctx['end_date']})
Sprint progress: {sprint_ctx['completed']}/{sprint_ctx['total']} issues done

You can search, create, and update issues. Always confirm before creating/modifying.
When uncertain, ask for clarification rather than guessing.
"""
        return system_prompt
```

Conversation memory stored in Redis (TTL = 24 hours):
```python
CONVERSATION_KEY = f"ai:conv:{user_id}:{session_id}"
# Store last N messages (sliding window, max 20 turns)
```

---

## 6. Plugin System

### 6.1 Plugin Architecture

Plugins are Python packages that register themselves with the app on startup. They can:
1. Add new API routes
2. Add new background tasks
3. Add new UI components (via a plugin manifest)
4. Subscribe to internal events
5. Extend issue fields

```python
# app/plugins/base.py
from abc import ABC, abstractmethod
from fastapi import FastAPI

class Plugin(ABC):
    name: str
    version: str
    description: str
    
    @abstractmethod
    def register(self, app: FastAPI, event_bus: EventBus):
        """Called on startup. Register routes, event handlers, etc."""
        ...
    
    def get_settings_schema(self) -> dict:
        """JSON Schema for org-level settings UI."""
        return {}
    
    def get_ui_manifest(self) -> dict:
        """Describes UI injection points for frontend."""
        return {}
```

**Example: Slack Plugin**
```python
# plugins/slack/plugin.py
class SlackPlugin(Plugin):
    name = "slack"
    version = "1.0.0"
    
    def register(self, app: FastAPI, event_bus: EventBus):
        # Add routes for OAuth flow
        from .router import router
        app.include_router(router, prefix="/plugins/slack")
        
        # Subscribe to events
        event_bus.subscribe("issue.created", self.on_issue_created)
        event_bus.subscribe("comment.added", self.on_comment_added)
    
    async def on_issue_created(self, event: IssueCreatedEvent):
        config = await self.get_org_config(event.org_id)
        if config.get("notify_channel"):
            await send_slack_message(config["webhook_url"], ...)
    
    def get_settings_schema(self):
        return {
            "type": "object",
            "properties": {
                "webhook_url": {"type": "string", "format": "uri"},
                "notify_channel": {"type": "string"},
                "events": {"type": "array", "items": {"type": "string"}}
            }
        }
```

---

### 6.2 Plugin Registry

```python
# app/plugins/registry.py
class PluginRegistry:
    def __init__(self):
        self._plugins: dict[str, Plugin] = {}
    
    def discover(self):
        """Auto-discover plugins from entry points."""
        import importlib.metadata
        for ep in importlib.metadata.entry_points(group="projecttool.plugins"):
            plugin_cls = ep.load()
            plugin = plugin_cls()
            self._plugins[plugin.name] = plugin
    
    def get_enabled_plugins(self, org: Organization) -> list[Plugin]:
        enabled = org.settings.get("enabled_plugins", [])
        return [p for name, p in self._plugins.items() if name in enabled]
    
    def register_all(self, app: FastAPI, event_bus: EventBus):
        for plugin in self._plugins.values():
            plugin.register(app, event_bus)
```

**Plugin entry point (pyproject.toml):**
```toml
[project.entry-points."projecttool.plugins"]
slack = "projecttool_slack:SlackPlugin"
github = "projecttool_github:GitHubPlugin"
```

---

### 6.3 Feature Flags

```python
# org.settings JSONB stores feature flags
{
  "features": {
    "ai_agent": true,
    "time_tracking": false,
    "doc_ai_search": false,
    "custom_fields": true
  },
  "ai": {
    "provider": "openai",
    "api_key": "sk-...",  # encrypted at rest
    "enabled": true
  },
  "enabled_plugins": ["slack", "github"]
}

# Backend guard
def require_feature(feature: str):
    def dependency(org: Organization = Depends(get_current_org)):
        if not org.settings.get("features", {}).get(feature):
            raise HTTPException(403, f"Feature '{feature}' is not enabled")
    return Depends(dependency)

@router.post("/ai/query", dependencies=[require_feature("ai_agent")])
async def ai_query(body: AIQueryRequest):
    ...
```

**Frontend feature flag hook:**
```typescript
const useFeatureFlag = (flag: string): boolean => {
  const { org } = useOrg();
  return org?.settings?.features?.[flag] ?? false;
};

// Usage
const aiEnabled = useFeatureFlag('ai_agent');
{aiEnabled && <AIPanel />}
```

---

## 7. Authentication System

### 7.1 Token Architecture

**Hybrid approach: Short-lived JWT access token + opaque refresh token**

| Token | Type | Storage | TTL | Purpose |
|-------|------|---------|-----|---------|
| Access | JWT (signed) | Memory (JS var) | 15 min | API calls |
| Refresh | Opaque (random) | httpOnly Cookie | 30 days | Get new access token |

**Why NOT pure JWT:**
- You can't revoke JWTs without a blocklist (defeats the purpose)
- Refresh tokens stored in DB allow instant logout / force-revoke

**Why NOT pure sessions:**
- JWTs are stateless — backend doesn't need DB hit on every request
- Good for horizontal scaling

```python
# Access token payload
{
  "sub": "user-uuid",
  "org": "org-uuid",
  "role": "admin",
  "exp": 1735000000  # 15 min
}

# Refresh token: random 32 bytes, stored hashed in sessions table
# Sent as httpOnly SameSite=Strict cookie

# On every API request:
# 1. Verify JWT signature + expiry
# 2. Extract user/org from claims (no DB hit)
# On access token expiry:
# 1. Frontend detects 401
# 2. POST /auth/refresh with cookie
# 3. Verify refresh token hash in sessions table
# 4. Issue new access token
```

---

### 7.2 LDAP Integration

LDAP doesn't issue tokens — it just validates credentials. Design:

```python
# POST /auth/ldap/login
# Body: {username, password}

async def ldap_login(username: str, password: str, org_id: UUID):
    ldap_config = await get_org_ldap_config(org_id)  # host, bind_dn, base_dn, etc.
    
    # 1. Bind with service account
    conn = ldap3.Connection(ldap_config.host, ldap_config.bind_dn, ldap_config.bind_pw)
    conn.bind()
    
    # 2. Search for user
    conn.search(ldap_config.base_dn, f"(uid={username})", attributes=["cn", "mail", "memberOf"])
    user_entry = conn.entries[0]
    
    # 3. Bind with user credentials (validates password)
    user_conn = ldap3.Connection(ldap_config.host, user_entry.entry_dn, password)
    if not user_conn.bind():
        raise InvalidCredentials()
    
    # 4. Get/create user in our DB from LDAP attributes
    email = str(user_entry.mail)
    display_name = str(user_entry.cn)
    
    user = await get_or_create_user(
        email=email,
        display_name=display_name,
        auth_provider="ldap",
        external_id=user_entry.entry_dn
    )
    
    # 5. Issue OUR tokens (same as local auth)
    return await create_session(user)
```

**Key insight:** LDAP only authenticates. We issue our own JWT/session after validation. LDAP users are in our `users` table with `auth_provider='ldap'`.

---

### 7.3 RBAC Design

```python
PERMISSIONS = {
    # Project permissions
    "issue:read":     ["viewer", "member", "admin", "owner"],
    "issue:create":   ["member", "admin", "owner"],
    "issue:update":   ["member", "admin", "owner"],
    "issue:delete":   ["admin", "owner"],
    "sprint:manage":  ["admin", "owner"],
    "project:admin":  ["admin", "owner"],
    
    # Org permissions
    "member:invite":  ["admin", "owner"],
    "billing:manage": ["owner"],
    "plugin:manage":  ["admin", "owner"],
}

# Effective role = max(org_membership.role, project_members.role)
# org: admin can do anything in their org
# project: member can do member-level things in that project

def check_permission(user_id, org_id, project_id, permission):
    org_role = get_org_role(user_id, org_id)
    project_role = get_project_role(user_id, project_id)
    effective_role = max_role(org_role, project_role)
    return effective_role in PERMISSIONS[permission]
```

---

## 8. DevOps & Deployment

### 8.1 Docker Setup

```yaml
# docker-compose.yml (development)
services:
  api:
    build: ./backend
    command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    volumes: [./backend:/app]
    env_file: [.env]
    depends_on: [db, redis]
    ports: ["8000:8000"]
  
  worker:
    build: ./backend
    command: celery -A app.workers.celery_app worker -Q default,high_priority,ai
    volumes: [./backend:/app]
    env_file: [.env]
    depends_on: [db, redis]
  
  beat:
    build: ./backend
    command: celery -A app.workers.celery_app beat --scheduler redbeat.RedBeatScheduler
    env_file: [.env]
    depends_on: [redis]
  
  frontend:
    build: ./frontend
    command: npm run dev
    volumes: [./frontend:/app]
    ports: ["3000:3000"]
  
  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: projecttool
      POSTGRES_USER: app
      POSTGRES_PASSWORD: secret
    volumes: [pgdata:/var/lib/postgresql/data]
    ports: ["5432:5432"]
  
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
  
  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    ports: ["9000:9000", "9001:9001"]

volumes:
  pgdata:
```

**Production Dockerfile (backend):**
```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir ".[prod]"

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY . .
RUN useradd --no-create-home --no-login appuser
USER appuser
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

---

### 8.2 CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/main.yml
on:
  push:
    branches: [main]
  pull_request:

jobs:
  test-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: pgvector/pgvector:pg16
        env: {POSTGRES_DB: test, POSTGRES_USER: test, POSTGRES_PASSWORD: test}
      redis:
        image: redis:7-alpine
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.12"}
      - run: pip install -e ".[test]"
      - run: pytest tests/ --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v4

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: {node-version: "20"}
      - run: npm ci
      - run: npm run type-check
      - run: npm run test
      - run: npm run build

  build-and-push:
    needs: [test-backend, test-frontend]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: registry.io/projecttool/api:${{ github.sha }}
  
  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/api api=registry.io/projecttool/api:${{ github.sha }}
          kubectl rollout status deployment/api
```

---

### 8.3 Observability

```python
# Structured logging with structlog
import structlog

logger = structlog.get_logger()

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    logger.info("request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=(time.time() - start) * 1000,
        user_id=getattr(request.state, "user_id", None),
        org_id=getattr(request.state, "org_id", None),
        trace_id=request.headers.get("X-Trace-ID")
    )
    return response
```

**Metrics stack:**
- **Prometheus** + **Grafana** for metrics (FastAPI exposes `/metrics`)
- **OpenTelemetry** for distributed tracing (export to Jaeger or OTLP)
- **Sentry** for error tracking
- **Loki** for log aggregation

**Key metrics to track:**
- `api_request_duration_seconds` (histogram, by endpoint)
- `api_request_total` (counter, by status)
- `celery_task_duration_seconds`
- `db_query_duration_seconds`
- `ai_agent_calls_total` / `ai_token_usage_total`
- `active_users_total` (gauge)

---

## 9. MVP Plan & Roadmap

### Phase 1 — MVP (Weeks 1–10)

**Goal:** Usable by a small dev team. Can replace GitHub Issues.

**Include:**
- Email/password auth + Google SSO
- Organizations + Projects
- Issues: create, update, status, priority, assignee, labels
- Comments (plain text first, rich text in Week 6)
- Basic Kanban board (status columns)
- Issue list with filters (status, assignee, priority)
- Activity log
- Email notifications (assignment, comment)
- Single-tenant deploy (multi-tenancy architecture, single org in Phase 1)
- Docker compose deploy

**Exclude from MVP:**
- Sprints/Scrum (Week 11+)
- AI agent
- Documentation system
- Webhooks
- Custom fields (basic ones hardcoded)
- LDAP
- Reports/charts

**Architecture simplification for MVP:**
- Synchronous everything (no Celery yet — use FastAPI background tasks)
- Skip Redis (use in-process cache)
- No plugin system yet
- Use S3 (real) from day 1 — don't cut corners on storage

**Milestone:** Team can manage a real project using the tool.

---

### Phase 2 — Planning & Collaboration (Weeks 11–20)

- Sprints (create, start, complete)
- Backlog view with sprint assignment
- Burndown chart
- Velocity tracking
- Custom fields (text, select, number, date)
- Story points / time estimates
- Rich text editor (Tiptap) for issue descriptions + comments
- Attachments
- Webhooks
- LDAP auth
- Celery + Redis (replace background tasks)
- Standup dashboard
- Search (FTS + trigram)

---

### Phase 3 — AI & Documentation (Weeks 21–32)

- Documentation system (Tiptap editor, versioning, tree nav)
- AI agent (read-only first: query, search, standup generation)
- RAG over docs + issues (pgvector)
- AI write actions (create/update issues)
- Sprint planning suggestions
- Delay prediction (based on velocity + remaining work)
- Embedding pipeline (Celery workers)
- Multi-LLM support (OpenAI, Anthropic, Ollama)

---

### Phase 4 — Enterprise & Ecosystem (Weeks 33+)

- Plugin architecture
- Slack integration (plugin)
- GitHub integration (auto-link PRs, close issues on merge)
- SAML/SSO
- Audit log export
- Data export (CSV, JSON)
- Admin dashboard (usage, billing)
- SLA/compliance features (data residency)
- White-labeling
- API rate limiting tiers

---

## 10. Scaling Plan

### Current Architecture Bottlenecks (at scale)

| Component | Bottleneck at | Solution |
|-----------|--------------|----------|
| FastAPI (4 workers) | ~500 req/s | Horizontal scaling, load balancer |
| PostgreSQL | ~10k concurrent connections | PgBouncer connection pooler |
| Search (FTS) | ~100k issues | Extract to OpenSearch/Typesense |
| AI embeddings | Latency on write path | Async Celery workers, dedicated GPU |
| WebSocket (real-time) | Sticky sessions | Redis pub/sub, separate WS service |

### Scaling Decisions

**Database:**
1. Read replicas for reports/search (report queries are expensive, don't run on primary)
2. Partition `activity_log` by month (this table grows fast)
3. PgBouncer in transaction mode between app and Postgres
4. At 50M+ issues, consider sharding by `org_id` (use Citus extension)

**Search at Scale:**
Phase 1–2: PostgreSQL FTS + `pg_trgm` (handles millions of issues fine)
Phase 3+: Typesense (simpler than Elasticsearch, fast, self-hosted) or OpenSearch

**Real-time at Scale:**
Phase 1: Long polling (no WebSocket infrastructure needed)
Phase 2: WebSocket with Redis pub/sub (all API instances subscribe to same Redis channels)
Phase 3+: Dedicated WebSocket service

**AI at Scale:**
- Embedding generation: GPU workers in separate Kubernetes deployment
- LLM calls: Rate limit per org (prevent abuse), queue in Redis
- pgvector: Fine up to ~10M vectors; migrate to Qdrant at scale

---

## 11. Risks & Tradeoffs

### Critical Risks

**1. Custom Fields in JSONB**
- **Pro**: Schema-less, flexible, one table for all issue types
- **Con**: Cannot do efficient `GROUP BY custom_field` without functional indexes
- **Mitigation**: For common aggregation fields (story points), keep them as real columns. Only truly custom fields go in JSONB.

**2. Single PostgreSQL Instance**
- **Risk**: Single point of failure, write bottleneck
- **Mitigation**: Use managed Postgres (RDS/Cloud SQL) with automatic failover. Read replicas from day 1 for reports.

**3. Modular Monolith Coupling**
- **Risk**: Over time, modules start importing each other directly and become a ball of mud
- **Mitigation**: Enforce module boundaries via a linter rule — modules can only communicate via the event bus or explicit service interfaces. Code review gates.

**4. AI Token Cost**
- **Risk**: Heavy AI usage can be expensive at org scale
- **Mitigation**: Per-org monthly token budget, feature-flagged, token usage tracking in `activity_log`, cost alerting

**5. Real-Time Complexity**
- **Risk**: WebSocket state management is hard (reconnection, missed events)
- **Mitigation**: Use `cursor`-based event streams. Client tracks last seen `activity_log.id`. On reconnect, pull delta. No complex socket state.

**6. LDAP Diversity**
- **Risk**: Every enterprise's LDAP is configured differently
- **Mitigation**: Make all LDAP attribute mappings configurable per org (`uid_attribute`, `email_attribute`, `group_attribute`)

### Key Tradeoff Summary

| Decision | Chosen | Alternative | Why |
|----------|--------|-------------|-----|
| Architecture | Modular monolith | Microservices | Speed of development, simpler ops |
| Primary DB | PostgreSQL | MongoDB | ACID, RLS, JSONB covers flexibility |
| Vector store | pgvector | Pinecone/Weaviate | No new infra, good enough at scale |
| Auth | JWT + opaque refresh | Pure session | Balance: stateless reads + revocable |
| API | REST | GraphQL | Simpler caching, easier webhooks |
| State | React Query + Zustand | Redux | Less boilerplate, clearer separation |
| Hierarchy | Single `issues` table | Separate tables | Uniform API, simpler queries |
| Search | FTS (Phase 1–2) | Elasticsearch | Avoid infra complexity early |

---

*Last updated: May 2026 | Version 1.0*
