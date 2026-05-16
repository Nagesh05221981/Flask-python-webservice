# My Service API — Architecture & Technical Documentation

## Table of Contents

1. [Overview](#1-overview)
2. [Technology Stack](#2-technology-stack)
3. [Project Structure](#3-project-structure)
4. [Architecture Diagram](#4-architecture-diagram)
5. [Database Schema](#5-database-schema)
6. [Authentication & Authorization](#6-authentication--authorization)
7. [API Reference](#7-api-reference)
8. [Request Lifecycle](#8-request-lifecycle)
9. [Data Flow](#9-data-flow)
10. [Configuration](#10-configuration)
11. [Running the Service](#11-running-the-service)
12. [Usage Examples](#12-usage-examples)
13. [Security Considerations](#13-security-considerations)
14. [Production Recommendations](#14-production-recommendations)

---

## 1. Overview

**My Service API** is a RESTful web service built with Python and FastAPI. It provides:

- Full CRUD operations for **Users** and **Products**
- Three authentication methods: username/password (JWT), API key, and OAuth
- Auto-generated interactive API documentation (Swagger UI / ReDoc)
- Ownership-based authorization (users can only modify their own resources)

---

## 2. Technology Stack

| Component        | Technology           | Version  | Purpose                                      |
|------------------|----------------------|----------|----------------------------------------------|
| Framework        | FastAPI              | 0.115.0  | Async web framework with auto OpenAPI docs   |
| ASGI Server      | Uvicorn              | 0.30.6   | High-performance async server                |
| ORM              | SQLAlchemy           | 2.0.35   | Database abstraction and query building      |
| Database         | SQLite               | built-in | Lightweight file-based relational database   |
| Validation       | Pydantic             | 2.9.2    | Request/response schema validation           |
| JWT              | python-jose          | 3.3.0    | JSON Web Token creation and verification     |
| Password Hashing | passlib + bcrypt     | 1.7.4    | Secure password hashing (bcrypt algorithm)   |
| HTTP Client      | httpx                | 0.27.2   | Async HTTP client (for future OAuth calls)   |
| Form Parsing     | python-multipart     | 0.0.12   | OAuth2 password form parsing                 |

---

## 3. Project Structure

```
my-service/
├── requirements.txt            # Pinned Python dependencies
├── app/
│   ├── __init__.py             # Package marker
│   ├── config.py               # Application configuration constants
│   ├── database.py             # SQLAlchemy engine, session factory, Base class
│   ├── models.py               # ORM models (User, Product)
│   ├── schemas.py              # Pydantic request/response schemas
│   ├── auth.py                 # Authentication logic (JWT, API key, password)
│   ├── main.py                 # FastAPI application entry point
│   └── routers/
│       ├── __init__.py         # Package marker
│       ├── auth_router.py      # /auth/* endpoints (register, login, OAuth)
│       ├── users_router.py     # /users/* endpoints (CRUD)
│       └── products_router.py  # /products/* endpoints (CRUD)
└── app.db                      # SQLite database file (auto-created at runtime)
```

### Layer Responsibilities

| Layer       | Files                           | Role                                               |
|-------------|---------------------------------|----------------------------------------------------|
| **Entry**   | `main.py`                       | Creates the FastAPI app, registers routers, boots DB |
| **Config**  | `config.py`                     | Centralized constants (secret key, DB URL, etc.)    |
| **Data**    | `database.py`, `models.py`      | ORM engine, session management, table definitions   |
| **Schema**  | `schemas.py`                    | Input validation and output serialization           |
| **Auth**    | `auth.py`                       | Password hashing, JWT lifecycle, dependency guards  |
| **Routes**  | `routers/*.py`                  | HTTP endpoint handlers grouped by domain            |

---

## 4. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT                                  │
│  (Browser / curl / Postman / Frontend App)                      │
└──────────────┬──────────────────────────────────────────────────┘
               │  HTTP Request
               ▼
┌──────────────────────────────────────────────────────────────────┐
│                      UVICORN (ASGI Server)                       │
│                      localhost:8000                               │
└──────────────┬───────────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────────┐
│                      FASTAPI APPLICATION                         │
│                                                                  │
│  ┌────────────┐  ┌────────────────┐  ┌───────────────────┐      │
│  │  Swagger UI │  │  ReDoc         │  │  OpenAPI JSON     │      │
│  │  /docs      │  │  /redoc        │  │  /openapi.json    │      │
│  └────────────┘  └────────────────┘  └───────────────────┘      │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    MIDDLEWARE STACK                        │   │
│  │  Request → Exception Handling → Router Dispatch           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                 DEPENDENCY INJECTION                       │   │
│  │                                                           │   │
│  │  get_db()  ──────────────►  SQLAlchemy Session            │   │
│  │  get_current_user()  ────►  Authenticated User object     │   │
│  │    ├─ Check X-API-Key header                              │   │
│  │    └─ Check Bearer JWT token                              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌────────────┐  ┌────────────────┐  ┌───────────────────┐      │
│  │ Auth Router │  │ Users Router   │  │ Products Router   │      │
│  │ /auth/*     │  │ /users/*       │  │ /products/*       │      │
│  └─────┬──────┘  └───────┬────────┘  └────────┬──────────┘      │
│        │                 │                     │                  │
└────────┼─────────────────┼─────────────────────┼─────────────────┘
         │                 │                     │
         ▼                 ▼                     ▼
┌──────────────────────────────────────────────────────────────────┐
│                    SQLALCHEMY ORM LAYER                           │
│                                                                  │
│  ┌──────────────┐          ┌──────────────────┐                  │
│  │  User Model   │ 1────N  │  Product Model    │                  │
│  │  (users)      │◄────────│  (products)       │                  │
│  └──────────────┘          └──────────────────┘                  │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                               ▼
                    ┌─────────────────┐
                    │   SQLite DB     │
                    │   (app.db)      │
                    └─────────────────┘
```

---

## 5. Database Schema

### Entity-Relationship Diagram

```
┌─────────────────────────┐       ┌──────────────────────────────┐
│         USERS            │       │          PRODUCTS             │
├─────────────────────────┤       ├──────────────────────────────┤
│ id          INTEGER  PK  │──┐   │ id           INTEGER  PK     │
│ username    TEXT  UNIQUE  │  │   │ name         TEXT  NOT NULL  │
│ email       TEXT  UNIQUE  │  │   │ description  TEXT  DEFAULT ''│
│ hashed_password TEXT      │  └──►│ owner_id     INTEGER  FK     │
│ is_active   BOOLEAN      │      │ price        REAL  NOT NULL  │
│ api_key     TEXT  UNIQUE  │      │ in_stock     BOOLEAN         │
└─────────────────────────┘       └──────────────────────────────┘
        1                                      N
        └──────────── owns ────────────────────┘
```

### Users Table

| Column          | Type    | Constraints              | Description                         |
|-----------------|---------|--------------------------|-------------------------------------|
| id              | INTEGER | PRIMARY KEY, AUTO-INCREMENT | Unique user identifier            |
| username        | TEXT    | UNIQUE, NOT NULL, INDEXED | Login username                     |
| email           | TEXT    | UNIQUE, NOT NULL, INDEXED | User email address                 |
| hashed_password | TEXT    | NOT NULL                  | bcrypt-hashed password             |
| is_active       | BOOLEAN | DEFAULT TRUE              | Soft-delete / deactivation flag    |
| api_key         | TEXT    | UNIQUE, INDEXED           | Auto-generated 32-byte URL-safe token |

### Products Table

| Column      | Type    | Constraints                    | Description                    |
|-------------|---------|--------------------------------|--------------------------------|
| id          | INTEGER | PRIMARY KEY, AUTO-INCREMENT    | Unique product identifier      |
| name        | TEXT    | NOT NULL, INDEXED              | Product name                   |
| description | TEXT    | DEFAULT ''                     | Product description            |
| price       | REAL    | NOT NULL                       | Product price                  |
| in_stock    | BOOLEAN | DEFAULT TRUE                   | Availability flag              |
| owner_id    | INTEGER | FOREIGN KEY → users.id, NOT NULL | The user who created this product |

### Relationships

- **User → Products**: One-to-Many. A user can own many products. Accessed via `user.products` (SQLAlchemy relationship).
- **Product → User**: Many-to-One. Each product belongs to one user. Accessed via `product.owner`.

---

## 6. Authentication & Authorization

The service supports **three** authentication methods, all resolved in a single dependency (`get_current_user`):

### 6.1 Authentication Flow Diagram

```
                    Incoming Request
                         │
                         ▼
              ┌─────────────────────┐
              │  X-API-Key header?  │
              └─────────┬───────────┘
                   YES  │  NO
                   ▼    │
         ┌─────────────┐│
         │ Lookup by    ││
         │ api_key col  ││
         └──────┬──────┘│
           Found│       │
           ▼    │       ▼
     ┌──────────┐  ┌─────────────────────┐
     │ Return   │  │ Authorization:       │
     │ User     │  │ Bearer <token> ?     │
     └──────────┘  └─────────┬───────────┘
                        YES  │  NO
                        ▼    │
              ┌─────────────┐│
              │ Decode JWT  ││
              │ Extract sub ││
              │ Lookup user ││
              └──────┬──────┘│
                Found│       │
                ▼    │       ▼
          ┌──────────┐  ┌──────────┐
          │ Return   │  │ 401      │
          │ User     │  │ Unauth.  │
          └──────────┘  └──────────┘
```

### 6.2 Method 1: Username/Password → JWT Token

1. Client `POST /auth/register` with `{username, email, password}`
2. Password is hashed with **bcrypt** and stored
3. Client `POST /auth/login` with form-data `username` + `password`
4. Server validates credentials, returns a signed **JWT** (HS256, 30-min expiry)
5. Client sends `Authorization: Bearer <token>` on subsequent requests

**JWT Payload:**
```json
{
  "sub": "testuser",
  "exp": 1700000000
}
```

### 6.3 Method 2: API Key

- Each user receives a unique API key on registration (`secrets.token_urlsafe(32)`)
- Client sends `X-API-Key: <key>` header
- Server looks up the key in the `users.api_key` column
- No expiration — valid as long as the user account is active

### 6.4 Method 3: Dummy OAuth

Simulates an OAuth 2.0 Authorization Code flow:

1. Client `GET /auth/oauth/login` → receives a fake authorization URL
2. Client `POST /auth/oauth/callback` with `{"code": "dummy-auth-code-123"}`
3. Server validates the code against a hardcoded map
4. If the user doesn't exist, auto-registers them
5. Returns a JWT access token

> **Note:** In production, replace the dummy provider with a real OAuth library (e.g., `authlib`) and redirect to Google/GitHub/etc.

### 6.5 Authorization Rules

| Resource  | Action         | Rule                                       |
|-----------|----------------|--------------------------------------------|
| Users     | List / Get     | Any authenticated user                     |
| Users     | Update         | Own account only (`current_user.id == user_id`) |
| Users     | Delete         | Own account only                           |
| Products  | Create         | Any authenticated user (becomes owner)     |
| Products  | List / Get     | Any authenticated user                     |
| Products  | Update         | Owner only (`product.owner_id == current_user.id`) |
| Products  | Delete         | Owner only                                 |

---

## 7. API Reference

### 7.1 Health

| Method | Path | Auth | Description          | Response |
|--------|------|------|----------------------|----------|
| GET    | `/`  | No   | Health check         | `{"status": "ok", "service": "my-service"}` |

### 7.2 Authentication (`/auth`)

| Method | Path                  | Auth | Request Body / Params                  | Response            |
|--------|-----------------------|------|----------------------------------------|---------------------|
| POST   | `/auth/register`      | No   | `{"username", "email", "password"}`    | `UserOut` (201)     |
| POST   | `/auth/login`         | No   | Form: `username` + `password`          | `Token` (200)       |
| GET    | `/auth/oauth/login`   | No   | —                                      | `{authorization_url, message}` |
| POST   | `/auth/oauth/callback`| No   | `{"code": "..."}`                      | `Token` (200)       |
| GET    | `/auth/me`            | Yes  | —                                      | `UserOut` (200)     |

### 7.3 Users (`/users`)

| Method | Path             | Auth | Request Body              | Response         |
|--------|------------------|------|---------------------------|------------------|
| GET    | `/users/`        | Yes  | Query: `skip`, `limit`    | `List[UserOut]`  |
| GET    | `/users/{id}`    | Yes  | —                         | `UserOut`        |
| PUT    | `/users/{id}`    | Yes  | `{"email?", "password?", "is_active?"}` | `UserOut` |
| DELETE | `/users/{id}`    | Yes  | —                         | 204 No Content   |

### 7.4 Products (`/products`)

| Method | Path               | Auth | Request Body                            | Response          |
|--------|--------------------|------|-----------------------------------------|-------------------|
| POST   | `/products/`       | Yes  | `{"name", "description?", "price", "in_stock?"}` | `ProductOut` (201) |
| GET    | `/products/`       | Yes  | Query: `skip`, `limit`                  | `List[ProductOut]` |
| GET    | `/products/{id}`   | Yes  | —                                       | `ProductOut`       |
| PUT    | `/products/{id}`   | Yes  | `{"name?", "description?", "price?", "in_stock?"}` | `ProductOut` |
| DELETE | `/products/{id}`   | Yes  | —                                       | 204 No Content     |

### 7.5 Response Schemas

**UserOut:**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "is_active": true,
  "api_key": "Tt1Zu1kYtO7It8LONWKKoWUv7NaaGNDIrIzO4ZKSmeI"
}
```

**ProductOut:**
```json
{
  "id": 1,
  "name": "Widget",
  "description": "A fine widget",
  "price": 9.99,
  "in_stock": true,
  "owner_id": 1
}
```

**Token:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### 7.6 Error Responses

| Status | Meaning              | Example Detail                                |
|--------|----------------------|-----------------------------------------------|
| 400    | Bad Request          | `"Username or email already registered"`      |
| 401    | Unauthorized         | `"Incorrect username or password"`            |
| 403    | Forbidden            | `"Can only update your own account"`          |
| 404    | Not Found            | `"Product not found"`                         |
| 422    | Validation Error     | Pydantic validation details (auto-generated)  |

---

## 8. Request Lifecycle

A typical authenticated request follows this path:

```
1. Client sends HTTP request
       │
2. Uvicorn receives → passes to FastAPI ASGI app
       │
3. FastAPI matches route via URL path + HTTP method
       │
4. Dependency Injection resolves parameters:
   │
   ├─ get_db()            → Opens a SQLAlchemy session
   │                        (yielded; closed in finally block)
   │
   └─ get_current_user()  → Extracts credentials from headers
       ├─ X-API-Key?      → DB lookup by api_key column
       └─ Bearer token?   → JWT decode → DB lookup by username
       │
5. Route handler executes business logic
   │
   ├─ Queries/mutates database via SQLAlchemy ORM
   ├─ Raises HTTPException on errors (400/401/403/404)
   └─ Returns Pydantic model (auto-serialized to JSON)
       │
6. FastAPI serializes response through response_model
   │
   ├─ Filters fields (e.g., hashed_password never exposed)
   └─ Validates output schema
       │
7. Response sent to client
       │
8. get_db() finally block closes the DB session
```

---

## 9. Data Flow

### Registration + Product Creation Flow

```
Client                     FastAPI                      SQLite
  │                           │                           │
  │  POST /auth/register      │                           │
  │  {username,email,password} │                           │
  │──────────────────────────►│                           │
  │                           │  Check duplicate          │
  │                           │──────────────────────────►│
  │                           │  bcrypt.hash(password)    │
  │                           │  INSERT INTO users        │
  │                           │──────────────────────────►│
  │                           │◄──────────────────────────│
  │  201 {id, username,       │                           │
  │       email, api_key}     │                           │
  │◄──────────────────────────│                           │
  │                           │                           │
  │  POST /auth/login         │                           │
  │  username=X&password=Y    │                           │
  │──────────────────────────►│                           │
  │                           │  SELECT user              │
  │                           │──────────────────────────►│
  │                           │  bcrypt.verify()          │
  │                           │  jwt.encode({sub:user})   │
  │  200 {access_token}       │                           │
  │◄──────────────────────────│                           │
  │                           │                           │
  │  POST /products/          │                           │
  │  Authorization: Bearer T  │                           │
  │  {name, price}            │                           │
  │──────────────────────────►│                           │
  │                           │  jwt.decode(T)            │
  │                           │  SELECT user by username  │
  │                           │──────────────────────────►│
  │                           │  INSERT INTO products     │
  │                           │──────────────────────────►│
  │  201 {id, name, price,    │                           │
  │       owner_id}           │                           │
  │◄──────────────────────────│                           │
```

---

## 10. Configuration

All configuration lives in `app/config.py`:

| Constant                    | Value                          | Description                              |
|-----------------------------|--------------------------------|------------------------------------------|
| `SECRET_KEY`                | `secrets.token_urlsafe(32)`    | JWT signing key (regenerated on restart) |
| `ALGORITHM`                 | `"HS256"`                      | JWT signing algorithm                    |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30`                         | JWT token lifetime                       |
| `DATABASE_URL`              | `"sqlite:///./app.db"`         | SQLAlchemy connection string             |

> **Important:** `SECRET_KEY` is regenerated every time the process restarts, which invalidates all existing tokens. For production, set this from an environment variable.

---

## 11. Running the Service

### Prerequisites

- Python 3.9+
- pip

### Setup

```bash
cd ~/my-service
pip install -r requirements.txt
```

### Start the Server

```bash
# Development (with auto-reload)
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Access Documentation

| URL                              | Description                    |
|----------------------------------|--------------------------------|
| `http://localhost:8000/docs`     | Swagger UI (interactive)       |
| `http://localhost:8000/redoc`    | ReDoc (read-only, detailed)    |
| `http://localhost:8000/openapi.json` | Raw OpenAPI 3.0 spec       |

---

## 12. Usage Examples

### Register a User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"s3cret"}'
```

### Login (get JWT)

```bash
curl -X POST http://localhost:8000/auth/login \
  -d "username=alice&password=s3cret"
```

### Use Bearer Token

```bash
TOKEN="eyJhbGciOi..."

curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### Use API Key

```bash
curl http://localhost:8000/products/ \
  -H "X-API-Key: Tt1Zu1kYtO7It8LONWKKoWUv7NaaGNDIrIzO4ZKSmeI"
```

### Create a Product

```bash
curl -X POST http://localhost:8000/products/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Gadget","price":24.99,"description":"A cool gadget"}'
```

### Update a Product

```bash
curl -X PUT http://localhost:8000/products/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"price":19.99}'
```

### Delete a Product

```bash
curl -X DELETE http://localhost:8000/products/1 \
  -H "Authorization: Bearer $TOKEN"
```

### OAuth Flow

```bash
# Step 1: Get the authorization URL
curl http://localhost:8000/auth/oauth/login

# Step 2: Exchange the code for a token
curl -X POST http://localhost:8000/auth/oauth/callback \
  -H "Content-Type: application/json" \
  -d '{"code":"dummy-auth-code-123"}'
```

---

## 13. Security Considerations

| Area              | Current Implementation            | Notes                                              |
|-------------------|-----------------------------------|----------------------------------------------------|
| Password Storage  | bcrypt hash via passlib           | Industry-standard; cost factor auto-managed        |
| JWT Signing       | HS256 symmetric                   | Adequate for single-service; use RS256 for multi-service |
| Token Expiry      | 30 minutes                        | Configurable in `config.py`                        |
| API Key           | 32-byte URL-safe random token     | No expiration; revoke by deactivating the user     |
| Input Validation  | Pydantic models with EmailStr     | Auto 422 on invalid input                          |
| SQL Injection     | SQLAlchemy ORM (parameterized)    | No raw SQL; safe by default                        |
| Authorization     | Ownership checks in route handlers| Users can only modify their own resources          |
| CORS              | Not configured                    | Add `CORSMiddleware` if serving a frontend         |
| Rate Limiting     | Not implemented                   | Add via middleware or reverse proxy for production  |
| HTTPS             | Not configured                    | Use a reverse proxy (nginx/Caddy) in production    |

---

## 14. Production Recommendations

1. **Persistent SECRET_KEY** — Load from environment variable or secrets manager instead of generating at startup
2. **Database** — Migrate from SQLite to PostgreSQL for concurrency and durability
3. **Migrations** — Add Alembic for schema versioning (`alembic init`, `alembic revision --autogenerate`)
4. **CORS** — Add `CORSMiddleware` with allowed origins for your frontend domain
5. **Rate Limiting** — Add `slowapi` or handle at the reverse proxy level
6. **HTTPS** — Terminate TLS at a reverse proxy (nginx, Caddy, or cloud load balancer)
7. **OAuth** — Replace dummy provider with `authlib` for Google/GitHub SSO
8. **API Key Rotation** — Add an endpoint to regenerate API keys
9. **Logging** — Structured logging with `structlog` or `loguru`
10. **Testing** — Add `pytest` + `httpx.AsyncClient` test suite
11. **Containerization** — Add `Dockerfile` and `docker-compose.yml`
12. **CI/CD** — GitHub Actions for lint, test, build, deploy pipeline
