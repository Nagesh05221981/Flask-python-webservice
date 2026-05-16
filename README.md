# My Service API

A RESTful web service built with **Python**, **FastAPI**, and **SQLite**. Provides user and product CRUD operations with three authentication methods and auto-generated Swagger documentation.

## Features

- **User & Product CRUD** — Full create, read, update, delete operations
- **Authentication** — Username/password (JWT), API key, and OAuth (dummy provider)
- **Authorization** — Ownership-based access control (users can only modify their own resources)
- **Swagger UI** — Interactive API docs auto-generated at `/docs`
- **API Test Suite** — Automated tests generated from the OpenAPI spec

## Tech Stack

| Component        | Technology        |
|------------------|-------------------|
| Framework        | FastAPI 0.115.0   |
| Server           | Uvicorn 0.30.6    |
| Database         | SQLite            |
| ORM              | SQLAlchemy 2.0.35 |
| Validation       | Pydantic 2.9.2    |
| Auth (JWT)       | python-jose 3.3.0 |
| Password Hashing | passlib + bcrypt  |

## Project Structure

```
my-service/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration constants
│   ├── database.py          # SQLAlchemy engine and session
│   ├── models.py            # User & Product ORM models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── auth.py              # Authentication logic
│   └── routers/
│       ├── auth_router.py   # /auth/* endpoints
│       ├── users_router.py  # /users/* endpoints
│       └── products_router.py # /products/* endpoints
├── Api_Tests/               # Automated API test suite
│   ├── core/                # Test framework (client, loader, builder)
│   ├── swagger/             # OpenAPI spec (openapi.yaml)
│   ├── config/              # Test settings
│   ├── schemas/             # Response validators with type checking
│   └── tests/               # Generated test cases
├── requirements.txt
├── ARCHITECTURE.md          # Detailed architecture & technical docs
└── README.md
```

## Quick Start

### 1. Install dependencies

```bash
cd my-service
pip install -r requirements.txt
```

### 2. Start the server

```bash
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Open Swagger UI

Visit [http://localhost:8000/docs](http://localhost:8000/docs) in your browser to explore and test all endpoints interactively.

## Authentication

The service supports three authentication methods. All protected endpoints accept either method:

### Username/Password (JWT)

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"s3cret"}'

# Login — returns a JWT access token
curl -X POST http://localhost:8000/auth/login \
  -d "username=alice&password=s3cret"

# Use the token
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer <TOKEN>"
```

### API Key

Each user receives a unique API key on registration. Pass it via the `X-API-Key` header:

```bash
curl http://localhost:8000/products/ \
  -H "X-API-Key: <YOUR_API_KEY>"
```

### OAuth (Dummy Provider)

Simulates an OAuth 2.0 Authorization Code flow for development:

```bash
# Get the authorization URL
curl http://localhost:8000/auth/oauth/login

# Exchange the code for a token
curl -X POST http://localhost:8000/auth/oauth/callback \
  -H "Content-Type: application/json" \
  -d '{"code":"dummy-auth-code-123"}'
```

## API Endpoints

### Health

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET    | `/`  | No   | Health check |

### Authentication

| Method | Path                   | Auth | Description                    |
|--------|------------------------|------|--------------------------------|
| POST   | `/auth/register`       | No   | Register a new user            |
| POST   | `/auth/login`          | No   | Login (returns JWT)            |
| GET    | `/auth/oauth/login`    | No   | Get OAuth authorization URL    |
| POST   | `/auth/oauth/callback` | No   | Exchange OAuth code for token  |
| GET    | `/auth/me`             | Yes  | Get current user profile       |

### Users

| Method | Path           | Auth | Description                  |
|--------|----------------|------|------------------------------|
| GET    | `/users/`      | Yes  | List all users (paginated)   |
| GET    | `/users/{id}`  | Yes  | Get user by ID               |
| PUT    | `/users/{id}`  | Yes  | Update user (own account only) |
| DELETE | `/users/{id}`  | Yes  | Delete user (own account only) |

### Products

| Method | Path              | Auth | Description                    |
|--------|-------------------|------|--------------------------------|
| POST   | `/products/`      | Yes  | Create a product               |
| GET    | `/products/`      | Yes  | List all products (paginated)  |
| GET    | `/products/{id}`  | Yes  | Get product by ID              |
| PUT    | `/products/{id}`  | Yes  | Update product (owner only)    |
| DELETE | `/products/{id}`  | Yes  | Delete product (owner only)    |

## Running Tests

The `Api_Tests/` directory contains an automated test suite that generates tests from the OpenAPI spec.

```bash
# Make sure the server is running first
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Install test dependencies and run
cd Api_Tests
pip install -r requirements.txt
python3 -m pytest tests/test_generated.py -v
```

Expected output:

```
tests/test_generated.py::test_api_endpoints[GET /]                      PASSED
tests/test_generated.py::test_api_endpoints[POST /auth/register]        PASSED
tests/test_generated.py::test_api_endpoints[POST /auth/login]           PASSED
tests/test_generated.py::test_api_endpoints[GET /auth/oauth/login]      PASSED
tests/test_generated.py::test_api_endpoints[POST /auth/oauth/callback]  PASSED
tests/test_generated.py::test_api_endpoints[GET /auth/me]               PASSED
tests/test_generated.py::test_api_endpoints[GET /users/]                PASSED
tests/test_generated.py::test_api_endpoints[GET /users/1]               PASSED
tests/test_generated.py::test_api_endpoints[PUT /users/1]               PASSED
tests/test_generated.py::test_api_endpoints[DELETE /users/1]            PASSED
tests/test_generated.py::test_api_endpoints[GET /products/]             PASSED
tests/test_generated.py::test_api_endpoints[POST /products/]            PASSED
tests/test_generated.py::test_api_endpoints[GET /products/1]            PASSED
tests/test_generated.py::test_api_endpoints[PUT /products/1]            PASSED
tests/test_generated.py::test_api_endpoints[DELETE /products/1]         PASSED

======================== 15 passed in 1.57s ========================
```

## Documentation

| URL                              | Description                    |
|----------------------------------|--------------------------------|
| `http://localhost:8000/docs`     | Swagger UI (interactive)       |
| `http://localhost:8000/redoc`    | ReDoc (read-only)              |
| `http://localhost:8000/openapi.json` | Raw OpenAPI 3.0 spec       |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Detailed architecture docs   |

## License

This project is for educational/development purposes.
