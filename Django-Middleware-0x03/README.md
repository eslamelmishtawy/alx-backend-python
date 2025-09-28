# Messaging App API

Full-stack ready messaging backend built with Django 4.2 and Django REST Framework. The service exposes conversation and message endpoints with nested routing, strong authentication defaults, and a custom user model tailored for richer profile data.

---

## Table of Contents
- [Project Layout](#project-layout)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Environment Configuration](#environment-configuration)
- [Authentication & Permissions](#authentication--permissions)
- [Domain Model Overview](#domain-model-overview)
- [Serialization & Validation](#serialization--validation)
- [ViewSets & Routing](#viewsets--routing)
- [API Endpoint Reference](#api-endpoint-reference)
- [Example Usage](#example-usage)
- [Database & Migrations](#database--migrations)
- [Testing](#testing)
- [Development Tips](#development-tips)
- [Deployment Checklist](#deployment-checklist)
- [Troubleshooting & FAQ](#troubleshooting--faq)
- [Design Decisions & Extension Points](#design-decisions--extension-points)
- [Next Steps](#next-steps)

## Project Layout

```
messaging_app/
├── manage.py                 # Django management entry point
├── db.sqlite3                # Default SQLite database (development only)
├── runserver.log             # Optional dev server log
├── chats/                    # Messaging domain app
│   ├── models.py             # User, Conversation, Message models
│   ├── serializers.py        # DRF serializers with nested relationships
│   ├── views.py              # ViewSets for conversations and messages
│   ├── urls.py               # Default and nested routers configuration
│   ├── admin.py              # Register models for Django admin (extend as needed)
│   ├── tests.py              # Placeholder for test suite
│   └── migrations/
│       └── 0001_initial.py   # Schema creation for chats app
└── messaging_app/
    ├── settings.py           # Project settings, installed apps, DRF defaults
    ├── urls.py               # Project URL configuration (admin + API)
    ├── asgi.py
    └── wsgi.py
```

Top-level repository files of interest:

- `requirements.txt` – shared dependency list for this and other projects (`Django`, `djangorestframework`, `drf-nested-routers`, `aiosqlite`).
- `python-*` directories – additional ALX exercises (not used by this service).

## Prerequisites

- Python **3.10+** (matches the ALX curriculum toolchain).
- pip 22+ (upgrade via `python -m pip install --upgrade pip`).
- SQLite 3 (bundled with Python). For PostgreSQL/MySQL, adjust `DATABASES` accordingly.
- Optional: `make`, `docker`, `httpie`, or Postman if you want scripted workflows—none required by default.

## Getting Started

1. **Clone & enter the project**
   ```bash
   git clone <repo-url>
   cd alx-backend-python/messaging_app
   ```

2. **Create & activate a virtualenv**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r ../requirements.txt
   ```

4. **Configure environment variables (recommended)**
   ```bash
   export DJANGO_DEBUG=True
   export DJANGO_SECRET_KEY='dev-secret-change-me'
   export DJANGO_ALLOWED_HOSTS='localhost,127.0.0.1'
   ```
   See [Environment Configuration](#environment-configuration) for wiring these into `settings.py`.

5. **Apply database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (admin access)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Seed sample data (optional)**
   ```bash
   python manage.py loaddata fixtures/sample_data.json
   ```
   > Fixtures are not bundled yet; create them later to fast-track QA.

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Log into the browsable API**
   Visit `http://127.0.0.1:8000/api/` and sign in via `http://127.0.0.1:8000/api-auth/login/`. Session authentication backs the UI, so login is required for mutating requests.

10. **Run Django checks & tests**
    ```bash
    python manage.py check
    python manage.py test
    ```
    Automated tests are placeholders for now; use them as scaffolding for future coverage.

## Environment Configuration

Development defaults live in `settings.py`, but production deployments should source values from the environment. Add logic near the top of `settings.py` similar to:

```python
import os

DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", SECRET_KEY)
ALLOWED_HOSTS = (
    os.getenv("DJANGO_ALLOWED_HOSTS", "")
    .replace(" ", "")
    .split(",")
    if not DEBUG
    else ["*"]
)
```

Other useful environment-driven settings:

- `DATABASE_URL` – pair with `dj-database-url` for easy Postgres/MySQL config.
- `CACHES` – configure Redis/Memcached when scaling chat throughput.
- `EMAIL_*` – hook up transactional emails for invites/reset flows.

Keep secrets outside version control (add `.env` to `.gitignore`).

## Authentication & Permissions

- `REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES']` → `IsAuthenticated`, enforcing login for all API access.
- `REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']` → session & basic authentication for flexibility across browsers and API clients.
- The REST framework login/logout views are exposed at `/api-auth/` for the browsable interface.

This setup supports quickly testing with session authentication locally while still honoring secure defaults in production.

## Domain Model Overview

### User (`chats.models.User`)
- Extends `AbstractUser` with a UUID primary key (`id`) and exposes `user_id` for consumers that expect explicit identifiers.
- Extra profile fields: `email` (unique), `phone_number`, `role` (guest/host/admin), `created_at` timestamp.
- Convenience helpers such as `full_name` and `has_password_set` retain compatibility with specs that look for password fields even though Django manages hashing internally.

### Conversation (`chats.models.Conversation`)
- UUID primary key plus derived `conversation_id` property.
- Many-to-many relationship with `User` via `participants` for flexible group chats.
- Timestamps (`created_at`) aid chronological sorting.

### Message (`chats.models.Message`)
- UUID primary key plus `message_id` property.
- Foreign keys to both `Conversation` and `User` (`sender`).
- `message_body` stores plain text; `sent_at` auto timestamps—ordering enforced via model meta.

### Entity Relationship Diagram (textual)

```
User (1) ────< participants >──── (M) Conversation (1) ────< messages >──── (M) Message
      ▲                                 ▲                                    |
      └────────────── sender ───────────┘                                    |
                                 (each message belongs to exactly one conversation)
```

Key notes:

- Conversations can have two or more participants; validation for minimum participants can be added in the serializer if needed.
- Deleting a user cascades deletes for their messages only if configured manually; by default Django protects them. Consider soft-deletion strategies for production.

## Serialization & Validation

| Serializer | Highlights |
|------------|------------|
| `UserSerializer` | Publishes `user_id`, standard profile fields, and is read-only for identifiers/timestamps. |
| `ConversationSerializer` | Accepts `participant_ids` for creation, nests participant and message data read-only, and exposes `latest_message` via `SerializerMethodField`. |
| `MessageSerializer` | Publishes `message_id`, requires `conversation_id` and `sender_id` on create, and validates that the sender participates in the selected conversation. |

Nested relationships leverage eager loading in the viewsets (`prefetch_related`, `select_related`) to minimize queries.

## ViewSets & Routing

- `ConversationViewSet`
  - Provides CRUD endpoints for conversations.
  - Supports search across participant usernames, first/last names, and emails using DRF’s `SearchFilter`.

- `MessageViewSet`
  - CRUD for messages with automatic ordering by `sent_at`.
  - Filtered by `conversation` query param or nested route parameter (`conversation_pk`).
  - Uses `OrderingFilter` to optionally control chronological direction.

### URL Configuration

Project-level URLs (`messaging_app/urls.py`) expose:

- `/admin/` – Django Admin.
- `/api/` – All chat endpoints.
- `/api-auth/` – DRF login/logout views.

App-level URLs (`chats/urls.py`) register both default and nested routers:

- `/api/conversations/`
- `/api/messages/`
- `/api/conversations/{conversation_id}/messages/`

The nested router is powered by `drf-nested-routers`, letting clients naturally traverse the conversation tree while keeping the standalone `/api/messages/` entry point for cross-conversation operations.

## API Endpoint Reference

| Endpoint | Methods | Description | Notes |
|----------|---------|-------------|-------|
| `/api/conversations/` | `GET`, `POST` | List all conversations (with nested participants/messages) or create a new one. | Use `search=` to filter by participant fields. POST requires `participant_ids`. |
| `/api/conversations/{conversation_id}/` | `GET`, `PUT`, `PATCH`, `DELETE` | Retrieve or mutate a single conversation. | PATCH recommended to avoid overriding participant list inadvertently. |
| `/api/conversations/{conversation_id}/messages/` | `GET`, `POST` | List messages for a conversation or create a new message scoped to it. | Query supports `ordering=sent_at` or `ordering=-sent_at`. POST requires `sender_id`. |
| `/api/messages/` | `GET`, `POST` | Cross-conversation list or create. | Filter by `?conversation=<uuid>`; same validation rules apply. |
| `/api/messages/{message_id}/` | `GET`, `PUT`, `PATCH`, `DELETE` | Inspect or edit a single message. | Respect conversation membership when reassigning. |
| `/api-auth/login/` | `GET`, `POST` | Obtain session cookie via DRF login form. | Requires CSRF token; accessible from the browsable API. |
| `/admin/` | `GET` | Django Admin dashboard. | Use superuser credentials. |

### Query Parameters

- `search` (conversations) – matches participant username/first/last name/email.
- `ordering` (messages) – accepts `sent_at` or `-sent_at`.
- `conversation` (messages) – filters the list endpoint to a conversation when using the non-nested route.

### Status Codes

- `200 OK` – Successful reads and updates.
- `201 CREATED` – Conversation/message created.
- `204 NO CONTENT` – Successful deletion responses.
- `400 BAD REQUEST` – Validation errors (e.g., sender not part of conversation).
- `401 UNAUTHORIZED` / `403 FORBIDDEN` – Missing or invalid authentication.
- `404 NOT FOUND` – Conversation or message does not exist.

## Example Usage

### Create a Conversation

```http
POST /api/conversations/
Content-Type: application/json

{
  "participant_ids": ["c4b2c314-0c1b-4b9d-86cf-9890c2312f09", "fd89d3b2-5ca4-406e-8cc0-1c2744e4f8e9"]
}
```

**Response**

```json
{
  "conversation_id": "7e22c9b7-a3f9-42de-9c98-3ac5f7eeeb65",
  "participants": [...],
  "messages": [],
  "latest_message": null,
  "created_at": "2025-09-20T22:07:19.463Z"
}
```

### Post a Message in a Conversation

```http
POST /api/conversations/7e22c9b7-a3f9-42de-9c98-3ac5f7eeeb65/messages/
Content-Type: application/json

{
  "conversation_id": "7e22c9b7-a3f9-42de-9c98-3ac5f7eeeb65",
  "sender_id": "c4b2c314-0c1b-4b9d-86cf-9890c2312f09",
  "message_body": "Hey team, standup in 10?"
}
```

**Response**

```json
{
  "message_id": "4f4cbaf9-0b5b-44df-9f92-44e1cc2790e4",
  "conversation": "7e22c9b7-a3f9-42de-9c98-3ac5f7eeeb65",
  "sender": {
    "user_id": "c4b2c314-0c1b-4b9d-86cf-9890c2312f09",
    "username": "jdoe",
    "first_name": "John",
    "last_name": "Doe",
    "email": "jdoe@example.com",
    "phone_number": null,
    "role": "guest",
    "created_at": "2025-09-20T21:48:03.218Z"
  },
  "message_body": "Hey team, standup in 10?",
  "sent_at": "2025-09-20T22:13:45.981Z"
}
```

The serializer-level validation ensures the `sender_id` belongs to the conversation; otherwise, a `400 BAD REQUEST` is returned with a descriptive error.

### Error Response Example

```json
{
  "conversation_id": ["This field is required."],
  "sender_id": ["Invalid pk \"abcd\" - object does not exist."],
  "non_field_errors": ["Sender must be a participant in the conversation."]
}
```

## Database & Migrations

- The project ships with an initial migration (`chats/migrations/0001_initial.py`) that creates the custom user, conversation, and message tables.
- SQLite is configured by default for ease of setup. For production, update `DATABASES` in `settings.py` and regenerate migrations as needed.
- To create new schema changes:
  ```bash
  python manage.py makemigrations chats
  python manage.py migrate
  ```

## Testing

- Placeholder tests reside in `chats/tests.py`. Extend this module with unit tests for models, serializers, and viewsets.
- Run the suite with:
  ```bash
  python manage.py test
  ```
- For more coverage, consider adding integration tests using DRF’s `APIClient` and factories (e.g., `factory_boy`).

## Development Tips

- Use Django Admin at `/admin/` to inspect conversations and messages during development.
- When modifying models, remember to run `python manage.py makemigrations` followed by `python manage.py migrate`.
- Enable DRF’s API docs or schema generators (e.g., `drf-spectacular`) for richer documentation if needed.
- The current authentication defaults block anonymous access; if you need public endpoints, override `permission_classes` per viewset or adjust the global settings carefully.
- Use `python manage.py shell_plus` (from `django-extensions`) if you add the dependency—it speeds up exploratory QA.

## Deployment Checklist

- [ ] Set `DJANGO_DEBUG=False` in production environments.
- [ ] Provide a secure `DJANGO_SECRET_KEY` (minimum 50 characters, random).
- [ ] Configure `ALLOWED_HOSTS` to include your domain/IP.
- [ ] Switch the database to PostgreSQL/MySQL using environment variables.
- [ ] Run `python manage.py collectstatic` if serving static files.
- [ ] Apply migrations on the target server.
- [ ] Configure a WSGI/ASGI server (Gunicorn, uvicorn) behind a reverse proxy (Nginx).
- [ ] Enable HTTPS (Let’s Encrypt, Cloudflare, etc.).
- [ ] Set up logging/monitoring, including DRF throttling or rate limits if exposing the API publicly.

## Troubleshooting & FAQ

**"ModuleNotFoundError: No module named 'django'"**
- Activate the virtual environment or ensure dependencies were installed with the correct interpreter.

**"ImproperlyConfigured: Requested setting INSTALLED_APPS, but settings are not configured"**
- Ensure `DJANGO_SETTINGS_MODULE=messaging_app.settings` is set when running scripts outside `manage.py`.

**"403 CSRF verification failed"**
- When using session auth from external clients, supply the CSRF token. For API automation, prefer token/basic auth.

**Search/ordering not working**
- Confirm `filters` are included in `DEFAULT_FILTER_BACKENDS` or rely on the per-view `filter_backends` already defined.

**UUID parsing errors in API calls**
- Double-check that UUIDs are hyphenated 36-character strings. Nested routes use `conversation_pk` that must match the conversation’s UUID.

## Design Decisions & Extension Points

- **Custom User Model from Day 0** – Avoids migration headaches when adding profile data; inheriting from `AbstractUser` preserves Django admin compatibility.
- **UUID Primary Keys** – Offer better security for public APIs by obscuring sequential IDs and ease client-side caching.
- **Nested Routers** – Provide natural REST semantics (`/conversations/<id>/messages/`) while keeping the flexibility of top-level message endpoints.
- **Serializer Validation** – Business rules (like participant membership) live close to the DTO layer, keeping views thin.

To extend the project:

- Add throttling (`REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES']`) for rate limiting.
- Introduce signals/webhooks when new messages arrive.
- Integrate Django Channels to broadcast messages in real time.
- Layer in message reactions or attachments by adding models and embedding them in serializers similarly to `MessageSerializer`.
- Add OpenAPI schema generation and publish documentation via Swagger/Redoc.

## Why These Choices & Alternatives

### Framework & Libraries

- Why Django + DRF?
  - Mature ecosystem, batteries-included admin, ORM, migrations, and a first-class API framework (DRF) with browsable UI and extensible auth/permissions.
  - Alternatives:
    - FastAPI + SQLAlchemy/Pydantic – great developer experience and performance for async; you assemble admin/auth/migrations.
    - Flask + Flask-RESTful/Flask-API – minimal and flexible; more boilerplate for auth/permissions/serialization.
    - GraphQL (Graphene/Strawberry) – client-driven queries; added complexity for authorization and caching chat timelines.

### Authentication & Permissions

- Why `IsAuthenticated` + `SessionAuthentication` (plus Basic for CLI/cURL)?
  - Secure-by-default browsing and quick dev/testing without provisioning tokens.
  - Alternatives:
    - TokenAuthentication (DRF Token) – simple static tokens; rotate manually and store securely.
    - JWT (`djangorestframework-simplejwt`) – stateless and scalable for SPA/mobile; add refresh/rotation, short TTLs, and secure storage.
    - OAuth2 (django-oauth-toolkit) – delegated auth and third-party integrations.
  - When to switch: public APIs, SPA/mobile clients, and multi-service systems benefit from JWT/OAuth2; server-rendered sites often prefer sessions.

### Data Modeling

- Why `AbstractUser` (vs `AbstractBaseUser` or default `User`)?
  - Keeps username/password flows and admin compatibility while enabling extra fields (email unique, phone, role). `AbstractBaseUser` offers full control but requires more setup/admin wiring.
  - Using the default `auth.User` hinders future changes and is hard to migrate away from.

- Why UUID primary keys?
  - Non-guessable IDs suit public APIs and distributed systems and allow client-side ID generation.
  - Alternatives: `AutoField/BigAutoField` (smaller, often faster), or ULIDs (sortable IDs with time component via third-party libs).

- Why M2M for `participants` (no through model)?
  - Simplicity where only membership matters.
  - Alternatives: a `through` model (`ConversationMembership`) to track roles, join timestamps, notification settings, or soft-deletes and to enforce uniqueness constraints (e.g., single 1:1 thread).

### Serializers & Validation

- Why nested data in responses?
  - Developer-friendly responses and fewer round-trips in common pages.
  - Alternatives: Hyperlinked or PK-only relationships for lean payloads with separate follow-up requests.

- Why membership validation in the serializer?
  - Centralizes business rules next to data marshalling; works across actions.
  - Alternatives: custom permissions at the view level or DB constraints/triggers for stronger guarantees (less friendly error UX).

### Routing & URLs

- Why `drf-nested-routers`?
  - Clean nested paths (`/conversations/{id}/messages/`) with minimal code while preserving top-level `/messages/`.
  - Alternatives: manual `path()` with explicit `get_queryset()` logic, or avoid nesting and rely solely on `?conversation=<id>` filter.

### Filtering

- Why `SearchFilter` and `OrderingFilter`?
  - Zero extra dependencies and quick wins.
  - Alternatives: `django-filter` for advanced lookups; Postgres FTS/SQLite FTS for message content search at scale.

### Settings & Configuration

- Why single settings module + env overrides?
  - Keeps local dev simple and production 12-factor friendly.
  - Alternatives: multiple settings files (`settings_dev.py`, `settings_prod.py`) selected via `DJANGO_SETTINGS_MODULE`, or use `django-environ/python-decouple` for typed env parsing.

### Database

- Why SQLite (dev)?
  - Zero-setup. Ideal for tutorials and small local datasets.
  - Alternatives: PostgreSQL for production (concurrency, JSONB, FTS); MySQL/MariaDB when mandated by infra.

### Deployment

- Why WSGI (Gunicorn + Nginx)?
  - Straightforward for sync apps.
  - Alternatives: ASGI (Uvicorn/Daphne) if adding websockets (Django Channels) or server-sent events.

## Security Considerations

- Enforce HTTPS; set `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, and appropriate `SameSite`.
- Narrow CORS with `django-cors-headers` if exposing to browsers.
- Prefer JWT/OAuth2 for SPA/mobile; avoid long-lived session cookies cross-origin.
- Rate-limit write endpoints and consider captcha/abuse controls where appropriate.
- Sanitize and virus-scan file uploads if/when attachments are added; store in object storage with signed URLs.

## Performance Tuning & Indexes

- Add composite indexes based on access patterns:
  - `(conversation_id, sent_at)` on `Message` to speed chronological queries in a conversation.
  - Partial indexes if you add soft-deletes or status flags.
- Use pagination for large lists; DRF supports Page/LimitOffset/Cursor pagination.
- Continue using `select_related`/`prefetch_related` (already applied) to avoid N+1.
- Cache hot endpoints per conversation or per user if needed; invalidate on writes.

## Next Steps

- Flesh out the automated test suite.
- Add rate limiting or throttling policies if exposed publicly.
- Consider websocket integrations (Channels) for real-time messaging.
- Expand `Message` to include attachments, read receipts, or status indicators.
- Automate deployment with GitHub Actions or similar CI/CD pipelines.

---

This README should equip new contributors with the context they need to understand the project structure, configure their environment, and extend the messaging API safely.
