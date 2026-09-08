# API Automation Framework — Step-by-Step Build Guide

Build a pytest-based API test framework from scratch for the FastAPI service at `localhost:8000`.

---

## API Endpoints Reference

Before you start, here are all the endpoints you will be testing:

| Method | Endpoint                  | Auth     | Request Body                                         | Response                  |
|--------|---------------------------|----------|------------------------------------------------------|---------------------------|
| GET    | `/`                       | None     | —                                                    | `{"status":"ok"}`         |
| POST   | `/auth/register`          | None     | `{"username","email","password"}` (JSON)             | User object, 201          |
| POST   | `/auth/login`             | None     | `{"username","password"}` (form data, NOT JSON)      | `{"access_token","token_type"}`, 200 |
| GET    | `/auth/me`                | Bearer   | —                                                    | User object, 200          |
| GET    | `/users/`                 | Bearer   | —                                                    | List of users, 200        |
| GET    | `/users/{id}`             | Bearer   | —                                                    | User object, 200          |
| PUT    | `/users/{id}`             | Bearer   | `{"email","password","is_active"}` (all optional)    | User object, 200          |
| DELETE | `/users/{id}`             | Bearer   | —                                                    | 204 No Content            |
| POST   | `/products/`              | Bearer   | `{"name","description","price","in_stock"}` (JSON)   | Product object, 201       |
| GET    | `/products/`              | Bearer   | —                                                    | List of products, 200     |
| GET    | `/products/{id}`          | Bearer   | —                                                    | Product object, 200       |
| PUT    | `/products/{id}`          | Bearer   | `{"name","description","price","in_stock"}` (all optional) | Product object, 200 |
| DELETE | `/products/{id}`          | Bearer   | —                                                    | 204 No Content            |

**Response shapes:**

- User object: `{"id", "username", "email", "is_active", "api_key"}`
- Product object: `{"id", "name", "description", "price", "in_stock", "owner_id"}`
- Token object: `{"access_token", "token_type"}`

**Business rules:**
- Users can only update/delete their own account (403 otherwise)
- Products can only be updated/deleted by their owner (403 otherwise)
- Duplicate username or email on register returns 400
- Invalid/missing fields return 422
- All `/users` and `/products` endpoints require a Bearer token (401 without)

---

## PHASE 1: Project Setup

### Step 1 — Create the folder structure

```bash
cd /Users/nageshallur/my-service/api_automation

mkdir -p config core utils schemas fixtures tests
touch config/__init__.py
touch core/__init__.py
touch utils/__init__.py
touch schemas/__init__.py
touch fixtures/__init__.py
touch tests/__init__.py
```

### Step 2 — Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Create `requirements.txt`

Create the file with these contents:

```
pytest
requests
pytest-html
jsonschema
```

Then install:

```bash
pip install -r requirements.txt
```

**What you should have now:**

```
api_automation/
├── venv/
├── requirements.txt
├── config/__init__.py
├── core/__init__.py
├── utils/__init__.py
├── schemas/__init__.py
├── fixtures/__init__.py
└── tests/__init__.py
```

---

## PHASE 2: Configuration

### Step 4 — Create `config/settings.py`

This file stores the base URL and default test credentials. Using `os.getenv()` lets you override values via environment variables when running against staging/prod.

```python
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
```

That's it. You only need the base URL for now.

**Why:** Every API call needs a base URL. Hardcoding it everywhere means changing it in 20 places when you switch environments. Put it in one place.

---

## PHASE 3: Utilities

### Step 5 — Create `utils/test_data.py`

This generates random test data so each test run creates unique users/products and doesn't collide with previous runs.

```python
import uuid


def generate_user():
    unique = uuid.uuid4().hex[:8]
    return {
        "username": f"user_{unique}",
        "password": "TestPass1234",
        "email": f"user_{unique}@test.com",
    }


def generate_product():
    unique = uuid.uuid4().hex[:8]
    return {
        "name": f"Product_{unique}",
        "description": f"Test product {unique}",
        "price": 19.99,
        "in_stock": True,
    }
```

**Why unique data:** If you hardcode `username: "testuser"`, the second test run fails because that user already exists in the database.

### Step 6 — Create `utils/assertions.py`

Reusable assertion helpers that give clear error messages when tests fail.

```python
def assert_status(response, expected):
    assert response.status_code == expected, (
        f"Expected {expected}, got {response.status_code}. "
        f"Body: {response.text}"
    )


def assert_json_has_keys(response, keys):
    data = response.json()
    for key in keys:
        assert key in data, f"Missing key '{key}' in response: {data}"


def assert_error(response, expected_status, detail_contains=None):
    assert_status(response, expected_status)
    if detail_contains:
        detail = response.json().get("detail", "")
        assert detail_contains.lower() in detail.lower(), (
            f"Expected '{detail_contains}' in detail, got: '{detail}'"
        )
```

**Why helpers:** Without `assert_status`, a failure just says `AssertionError`. With it, you see: `Expected 201, got 400. Body: {"detail":"Username already registered"}` — much easier to debug.

---

## PHASE 4: API Client

### Step 7 — Create `core/api_client.py`

This is the heart of the framework. A class that wraps `requests.Session` with one method per API endpoint.

```python
import requests
from config.settings import BASE_URL


class ApiClient:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.token = None

    def set_token(self, token):
        self.token = token
        self.session.headers["Authorization"] = f"Bearer {token}"

    def clear_auth(self):
        self.token = None
        self.session.headers.pop("Authorization", None)

    # --- Auth ---

    def register(self, payload):
        return self.session.post(f"{self.base_url}/auth/register", json=payload)

    def login(self, username, password):
        # IMPORTANT: login uses form data (data=), NOT json=
        return self.session.post(
            f"{self.base_url}/auth/login",
            data={"username": username, "password": password},
        )

    def get_me(self):
        return self.session.get(f"{self.base_url}/auth/me")

    # --- Users ---

    def list_users(self, skip=0, limit=20):
        return self.session.get(
            f"{self.base_url}/users/", params={"skip": skip, "limit": limit}
        )

    def get_user(self, user_id):
        return self.session.get(f"{self.base_url}/users/{user_id}")

    def update_user(self, user_id, payload):
        return self.session.put(f"{self.base_url}/users/{user_id}", json=payload)

    def delete_user(self, user_id):
        return self.session.delete(f"{self.base_url}/users/{user_id}")

    # --- Products ---

    def create_product(self, payload):
        return self.session.post(f"{self.base_url}/products/", json=payload)

    def list_products(self, skip=0, limit=20):
        return self.session.get(
            f"{self.base_url}/products/", params={"skip": skip, "limit": limit}
        )

    def get_product(self, product_id):
        return self.session.get(f"{self.base_url}/products/{product_id}")

    def update_product(self, product_id, payload):
        return self.session.put(
            f"{self.base_url}/products/{product_id}", json=payload
        )

    def delete_product(self, product_id):
        return self.session.delete(f"{self.base_url}/products/{product_id}")

    # --- Health ---

    def health_check(self):
        return self.session.get(f"{self.base_url}/")
```

**Key things to understand:**
- `requests.Session()` persists headers across calls — once you `set_token()`, every subsequent request includes the Bearer token automatically
- `login()` uses `data=` (form-encoded) not `json=` — the FastAPI endpoint expects `OAuth2PasswordRequestForm` which reads form data
- Each method returns the raw `requests.Response` object — the test decides what to assert

---

## PHASE 5: Schema Validators

### Step 8 — Create `schemas/validators.py`

These functions check that API responses contain the expected fields.

```python
USER_KEYS = ["id", "username", "email", "is_active", "api_key"]
PRODUCT_KEYS = ["id", "name", "description", "price", "in_stock", "owner_id"]
TOKEN_KEYS = ["access_token", "token_type"]


def is_valid_user(data):
    return all(key in data for key in USER_KEYS)


def is_valid_product(data):
    return all(key in data for key in PRODUCT_KEYS)


def is_valid_token(data):
    return all(key in data for key in TOKEN_KEYS)
```

**Why:** Without this, you only check status codes. A 200 with `{"id": 1}` (missing fields) would pass. Validators catch that.

---

## PHASE 6: Fixtures

Fixtures are pytest's way of setting up test preconditions. They form a chain — each one builds on the previous.

### Step 9 — Create `fixtures/auth_fixtures.py`

```python
import pytest
from core.api_client import ApiClient
from utils.test_data import generate_user


@pytest.fixture
def client():
    """Return a fresh ApiClient instance (no auth)."""
    return ApiClient()


@pytest.fixture
def registered_user(client):
    """Register a new random user. Returns user data dict with password included."""
    user_data = generate_user()
    response = client.register(user_data)
    assert response.status_code == 201
    result = response.json()
    # Keep the password so we can login later
    result["password"] = user_data["password"]
    return result


@pytest.fixture
def authenticated_client(client, registered_user):
    """Return an ApiClient that is logged in with a Bearer token."""
    response = client.login(registered_user["username"], registered_user["password"])
    assert response.status_code == 200
    token = response.json()["access_token"]
    client.set_token(token)
    return client
```

**How the chain works:**
1. A test requests `authenticated_client`
2. pytest sees it depends on `client` and `registered_user`
3. `registered_user` depends on `client` too — pytest passes the same `client` instance to both
4. Result: a client that has a registered user and a valid Bearer token

### Step 10 — Create `fixtures/data_fixtures.py`

```python
import pytest
from utils.test_data import generate_product


@pytest.fixture
def created_product(authenticated_client):
    """Create a product owned by the authenticated user. Returns product data dict."""
    product_data = generate_product()
    response = authenticated_client.create_product(product_data)
    assert response.status_code == 201
    return response.json()
```

### Step 11 — Create `conftest.py` (in the project root, NOT inside tests/)

```python
from fixtures.auth_fixtures import *
from fixtures.data_fixtures import *
```

**Why:** pytest automatically loads `conftest.py`. The wildcard imports make all fixtures available to every test file without explicit imports.

---

## PHASE 7: Pytest Config

### Step 12 — Create `pytest.ini`

```ini
[pytest]
testpaths = tests
markers =
    smoke: quick health check
    auth: authentication tests
    users: user CRUD tests
    products: product CRUD tests
    negative: error and edge case tests
```

**Why markers:** They let you run subsets of tests. `pytest -m smoke` runs only smoke tests.

---

## PHASE 8: Test Files

Now write the actual tests. Start with the simplest and build up.

### Step 13 — Create `tests/test_health.py`

```python
import pytest
from utils.assertions import assert_status


@pytest.mark.smoke
def test_healthcheck(client):
    response = client.health_check()
    assert_status(response, 200)
```

**Checkpoint:** Start the service and run this one test now to verify your setup works:

```bash
# Terminal 1 — start the service
cd /Users/nageshallur/my-service
uvicorn app.main:app --reload

# Terminal 2 — run the test
cd /Users/nageshallur/my-service/api_automation
source venv/bin/activate
pytest tests/test_health.py -v
```

You should see `PASSED`. If not, fix the issue before moving on.

### Step 14 — Create `tests/test_auth.py`

```python
import pytest
from utils.assertions import assert_status, assert_json_has_keys, assert_error
from utils.test_data import generate_user
from schemas.validators import is_valid_user, is_valid_token


@pytest.mark.auth
class TestRegister:

    def test_register_success(self, client):
        """Register a new user — expect 201 and valid user object."""
        user = generate_user()
        response = client.register(user)
        assert_status(response, 201)
        assert is_valid_user(response.json())

    def test_register_duplicate_username(self, client, registered_user):
        """Register with an already-taken username — expect 400."""
        duplicate = {
            "username": registered_user["username"],
            "email": "other@test.com",
            "password": "TestPass123",
        }
        response = client.register(duplicate)
        assert_status(response, 400)

    def test_register_duplicate_email(self, client, registered_user):
        """Register with an already-taken email — expect 400."""
        duplicate = {
            "username": "someone_else",
            "email": registered_user["email"],
            "password": "TestPass123",
        }
        response = client.register(duplicate)
        assert_status(response, 400)


@pytest.mark.auth
class TestLogin:

    def test_login_success(self, client, registered_user):
        """Login with valid credentials — expect 200 and token."""
        response = client.login(registered_user["username"], registered_user["password"])
        assert_status(response, 200)
        assert is_valid_token(response.json())

    def test_login_wrong_password(self, client, registered_user):
        """Login with wrong password — expect 401."""
        response = client.login(registered_user["username"], "WrongPass999")
        assert_status(response, 401)

    def test_login_nonexistent_user(self, client):
        """Login with a user that doesn't exist — expect 401."""
        response = client.login("nouser_xyz", "nopass")
        assert_status(response, 401)


@pytest.mark.auth
class TestMe:

    def test_get_me(self, authenticated_client, registered_user):
        """Get current user profile — expect 200 and correct username."""
        response = authenticated_client.get_me()
        assert_status(response, 200)
        assert response.json()["username"] == registered_user["username"]

    def test_get_me_no_auth(self, client):
        """Get /auth/me without token — expect 401."""
        response = client.get_me()
        assert_status(response, 401)
```

**Checkpoint:** `pytest tests/test_auth.py -v` — expect 8 passed.

### Step 15 — Create `tests/test_users.py`

```python
import pytest
from utils.assertions import assert_status, assert_error
from utils.test_data import generate_user
from schemas.validators import is_valid_user


@pytest.mark.users
class TestListUsers:

    def test_list_users(self, authenticated_client):
        """List all users — expect 200 and a list."""
        response = authenticated_client.list_users()
        assert_status(response, 200)
        assert isinstance(response.json(), list)

    def test_list_users_no_auth(self, client):
        """List users without token — expect 401."""
        response = client.list_users()
        assert_status(response, 401)


@pytest.mark.users
class TestGetUser:

    def test_get_user_by_id(self, authenticated_client, registered_user):
        """Get a user by ID — expect 200 and valid user object."""
        user_id = registered_user["id"]
        response = authenticated_client.get_user(user_id)
        assert_status(response, 200)
        assert is_valid_user(response.json())

    def test_get_user_not_found(self, authenticated_client):
        """Get a user that doesn't exist — expect 404."""
        response = authenticated_client.get_user(99999)
        assert_status(response, 404)


@pytest.mark.users
class TestUpdateUser:

    def test_update_own_email(self, authenticated_client, registered_user):
        """Update your own email — expect 200 and updated value."""
        user_id = registered_user["id"]
        response = authenticated_client.update_user(user_id, {"email": "new@test.com"})
        assert_status(response, 200)
        assert response.json()["email"] == "new@test.com"

    def test_update_other_user_forbidden(self, authenticated_client):
        """Try to update another user's account — expect 403 or 404."""
        response = authenticated_client.update_user(1, {"email": "hack@test.com"})
        assert response.status_code in [403, 404]


@pytest.mark.users
class TestDeleteUser:

    def test_delete_own_account(self, client):
        """Register a user, login, delete self — expect 204."""
        user_data = generate_user()
        reg = client.register(user_data)
        assert_status(reg, 201)
        user_id = reg.json()["id"]

        login = client.login(user_data["username"], user_data["password"])
        client.set_token(login.json()["access_token"])

        response = client.delete_user(user_id)
        assert_status(response, 204)

    def test_delete_other_user_forbidden(self, authenticated_client):
        """Try to delete another user — expect 403 or 404."""
        response = authenticated_client.delete_user(1)
        assert response.status_code in [403, 404]
```

**Checkpoint:** `pytest tests/test_users.py -v` — expect 7 passed.

### Step 16 — Create `tests/test_products.py`

```python
import pytest
from utils.assertions import assert_status
from utils.test_data import generate_product
from schemas.validators import is_valid_product


@pytest.mark.products
class TestCreateProduct:

    def test_create_product(self, authenticated_client):
        """Create a new product — expect 201 and valid product object."""
        product = generate_product()
        response = authenticated_client.create_product(product)
        assert_status(response, 201)
        assert is_valid_product(response.json())

    def test_create_product_no_auth(self, client):
        """Create product without token — expect 401."""
        product = generate_product()
        response = client.create_product(product)
        assert_status(response, 401)


@pytest.mark.products
class TestListProducts:

    def test_list_products(self, authenticated_client):
        """List all products — expect 200 and a list."""
        response = authenticated_client.list_products()
        assert_status(response, 200)
        assert isinstance(response.json(), list)


@pytest.mark.products
class TestGetProduct:

    def test_get_product_by_id(self, authenticated_client, created_product):
        """Get a product by ID — expect 200 and valid product object."""
        product_id = created_product["id"]
        response = authenticated_client.get_product(product_id)
        assert_status(response, 200)
        assert is_valid_product(response.json())

    def test_get_product_not_found(self, authenticated_client):
        """Get a product that doesn't exist — expect 404."""
        response = authenticated_client.get_product(99999)
        assert_status(response, 404)


@pytest.mark.products
class TestUpdateProduct:

    def test_update_own_product(self, authenticated_client, created_product):
        """Update your own product — expect 200 and updated values."""
        product_id = created_product["id"]
        response = authenticated_client.update_product(
            product_id, {"name": "Updated Name", "price": 99.99}
        )
        assert_status(response, 200)
        assert response.json()["name"] == "Updated Name"
        assert response.json()["price"] == 99.99


@pytest.mark.products
class TestDeleteProduct:

    def test_delete_own_product(self, authenticated_client, created_product):
        """Delete your own product — expect 204, then verify it's gone."""
        product_id = created_product["id"]
        response = authenticated_client.delete_product(product_id)
        assert_status(response, 204)

        # Confirm it's deleted
        response = authenticated_client.get_product(product_id)
        assert_status(response, 404)
```

**Checkpoint:** `pytest tests/test_products.py -v` — expect 6 passed.

### Step 17 — Create `tests/test_negative.py`

```python
import pytest
from utils.assertions import assert_status


@pytest.mark.negative
class TestAuthNegative:

    def test_register_missing_fields(self, client):
        """Register with missing fields — expect 422."""
        response = client.register({"username": "onlyname"})
        assert response.status_code == 422

    def test_register_invalid_email(self, client):
        """Register with an invalid email format — expect 422."""
        response = client.register({
            "username": "baduser",
            "email": "not-an-email",
            "password": "TestPass123",
        })
        assert response.status_code == 422

    def test_login_empty_credentials(self, client):
        """Login with empty strings — expect 401 or 422."""
        response = client.login("", "")
        assert response.status_code in [401, 422]


@pytest.mark.negative
class TestProductsNegative:

    def test_create_product_missing_name(self, authenticated_client):
        """Create product without name — expect 422."""
        response = authenticated_client.create_product({"price": 10.0})
        assert response.status_code == 422

    def test_create_product_missing_price(self, authenticated_client):
        """Create product without price — expect 422."""
        response = authenticated_client.create_product({"name": "No Price"})
        assert response.status_code == 422


@pytest.mark.negative
class TestUnauthorized:

    def test_list_users_no_auth(self, client):
        """Access /users without token — expect 401."""
        response = client.list_users()
        assert_status(response, 401)

    def test_create_product_no_auth(self, client):
        """Create product without token — expect 401."""
        response = client.create_product({"name": "X", "price": 1.0})
        assert_status(response, 401)

    def test_get_me_no_auth(self, client):
        """Access /auth/me without token — expect 401."""
        response = client.get_me()
        assert_status(response, 401)

    def test_delete_user_no_auth(self, client):
        """Delete user without token — expect 401."""
        response = client.delete_user(1)
        assert_status(response, 401)
```

**Checkpoint:** `pytest tests/test_negative.py -v` — expect 9 passed.

---

## PHASE 9: Run Everything

### Step 18 — Start the service

```bash
cd /Users/nageshallur/my-service
uvicorn app.main:app --reload
```

### Step 19 — Run all tests

```bash
cd /Users/nageshallur/my-service/api_automation
source venv/bin/activate
pytest -v
```

### Step 20 — Run by marker

```bash
pytest -m smoke -v          # just health check
pytest -m auth -v           # just auth tests
pytest -m users -v          # just user tests
pytest -m products -v       # just product tests
pytest -m negative -v       # just negative tests
```

### Step 21 — Generate HTML report

```bash
pytest -v --html=report.html --self-contained-html
```

Open `report.html` in a browser.

---

## Final Structure

```
api_automation/
├── config/
│   ├── __init__.py
│   └── settings.py              ← Step 4
├── core/
│   ├── __init__.py
│   └── api_client.py            ← Step 7
├── utils/
│   ├── __init__.py
│   ├── test_data.py             ← Step 5
│   └── assertions.py            ← Step 6
├── schemas/
│   ├── __init__.py
│   └── validators.py            ← Step 8
├── fixtures/
│   ├── __init__.py
│   ├── auth_fixtures.py         ← Step 9
│   └── data_fixtures.py         ← Step 10
├── tests/
│   ├── __init__.py
│   ├── test_health.py           ← Step 13 (1 test)
│   ├── test_auth.py             ← Step 14 (8 tests)
│   ├── test_users.py            ← Step 15 (7 tests)
│   ├── test_products.py         ← Step 16 (6 tests)
│   └── test_negative.py         ← Step 17 (9 tests)
├── conftest.py                  ← Step 11
├── pytest.ini                   ← Step 12
├── requirements.txt             ← Step 3
└── venv/
```

**Total: 31 tests**

---

## Quick Reference

| Command                              | What It Does                  |
|--------------------------------------|-------------------------------|
| `pytest -v`                          | Run all tests, verbose        |
| `pytest -m smoke -v`                 | Run only smoke tests          |
| `pytest tests/test_auth.py -v`       | Run one file                  |
| `pytest -k "test_login" -v`         | Run tests matching a keyword  |
| `pytest -v -s`                       | Show print() output           |
| `pytest --html=report.html`         | Generate HTML report          |
| `BASE_URL=http://staging:8000 pytest`| Run against another env       |

---

## Common Gotchas

1. **Login uses form data, not JSON** — `data={"username":...}` not `json={"username":...}`. The FastAPI endpoint uses `OAuth2PasswordRequestForm` which reads form-encoded bodies.

2. **Always use unique test data** — `generate_user()` uses `uuid4` so each test creates a unique user. Never hardcode usernames.

3. **Fixture chain matters** — `authenticated_client` depends on `registered_user` which depends on `client`. If you use `authenticated_client` in a test, all three fixtures run automatically.

4. **`conftest.py` must be in the project root** — not inside `tests/`. That's how fixtures become available to all test files.

5. **Service must be running** — these are integration tests that hit real HTTP endpoints. Start `uvicorn app.main:app --reload` before running tests.

---

## PHASE 10: Continue on Failure (Don't Stop at First Failure)

By default, pytest runs all tests even if some fail. But if you ever used `pytest -x`, that stops at the first failure. Here's how to control this:

### Step 22 — Update `pytest.ini` to never stop early

Add `addopts` to your `pytest.ini`:

```ini
[pytest]
testpaths = tests
addopts = --tb=short -v
markers =
    smoke: quick health check
    auth: authentication tests
    users: user CRUD tests
    products: product CRUD tests
    negative: error and edge case tests
```

**What each flag does:**

| Flag | Meaning |
|------|---------|
| (no `-x` flag) | Runs ALL tests even if some fail (this is the default) |
| `--tb=short` | Shows a short traceback on failure (not the full wall of text) |
| `-v` | Verbose — shows each test name and PASSED/FAILED |

**Other `--tb` options you should know:**

| Value | When to use |
|-------|-------------|
| `--tb=short` | Default for CI — shows the assert line and a few lines of context |
| `--tb=long` | Deep debugging — shows full traceback with local variables |
| `--tb=line` | Quick summary — one line per failure |
| `--tb=no` | Just PASSED/FAILED, no traceback at all |

**Try it yourself:** Intentionally break a test (change an expected status from 200 to 999), run `pytest`, and confirm it continues running the remaining tests.

---

## PHASE 11: Production-Grade Logging

### Step 23 — Update `requirements.txt`

Add this line:

```
allure-pytest
```

Your full `requirements.txt` should now be:

```
pytest
requests
pytest-html
jsonschema
allure-pytest
```

Install:

```bash
pip install -r requirements.txt
```

### Step 24 — Create `utils/logger.py`

Build a centralized logger that writes to both the console AND a log file.

```python
import logging
import os
from datetime import datetime


def get_logger(name):
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Create logs directory
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports", "logs")
    os.makedirs(log_dir, exist_ok=True)

    # Log file named by date
    log_file = os.path.join(log_dir, f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

    # File handler — captures DEBUG and above (everything)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    # Console handler — captures INFO and above (cleaner output)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Format
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-5s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
```

**What this gives you:**
- Console shows INFO-level messages (clean, readable)
- Log file captures everything including DEBUG (request payloads, response bodies)
- Each test run creates a timestamped log file — you can compare runs
- In CI/CD, the log file becomes a downloadable artifact for debugging

### Step 25 — Add logging to `core/api_client.py`

Modify your existing `api_client.py` to log every request and response. The key changes:

1. Import `get_logger` and `time` at the top
2. Add a private `_request()` method that all endpoint methods call
3. `_request()` logs the method, URL, payload, status code, and response time
4. Each endpoint method becomes a one-liner calling `_request()`

Here is what to change:

**At the top, add these imports:**

```python
import time
from utils.logger import get_logger

logger = get_logger("api_client")
```

**Add these three private methods to the `ApiClient` class:**

```python
def _log_request(self, method, url, **kwargs):
    logger.info(f"REQUEST  {method} {url}")
    if "json" in kwargs:
        logger.debug(f"  Payload: {kwargs['json']}")
    if "data" in kwargs:
        logger.debug(f"  Form data: {kwargs['data']}")
    if "params" in kwargs:
        logger.debug(f"  Params: {kwargs['params']}")

def _log_response(self, response, elapsed_ms):
    logger.info(f"RESPONSE {response.status_code} ({elapsed_ms}ms)")
    logger.debug(f"  Body: {response.text[:500]}")

def _request(self, method, path, **kwargs):
    url = f"{self.base_url}{path}"
    self._log_request(method, url, **kwargs)
    start = time.time()
    response = self.session.request(method, url, **kwargs)
    elapsed_ms = int((time.time() - start) * 1000)
    self._log_response(response, elapsed_ms)
    return response
```

**Then change each endpoint method to use `_request()`.** For example:

```python
# BEFORE
def register(self, payload):
    return self.session.post(f"{self.base_url}/auth/register", json=payload)

# AFTER
def register(self, payload):
    return self._request("POST", "/auth/register", json=payload)
```

Do this for every method: `register`, `login`, `get_me`, `list_users`, `get_user`, `update_user`, `delete_user`, `create_product`, `list_products`, `get_product`, `update_product`, `delete_product`, `health_check`.

**Why `_request()`:** Instead of repeating logging code in 13 methods, you put it in one place. Every API call now automatically gets logged with timing.

### Step 26 — Add test lifecycle logging to `conftest.py`

Update your `conftest.py` to log the start/end of every test and capture failures:

```python
from utils.logger import get_logger
from fixtures.auth_fixtures import *
from fixtures.data_fixtures import *

logger = get_logger("test_runner")


def pytest_runtest_setup(item):
    logger.info(f"{'='*60}")
    logger.info(f"START: {item.nodeid}")
    logger.info(f"{'='*60}")


def pytest_runtest_teardown(item):
    logger.info(f"END:   {item.nodeid}")


def pytest_runtest_makereport(item, call):
    if call.when == "call":
        if call.excinfo is not None:
            logger.error(f"FAILED: {item.nodeid}")
            logger.error(f"  Error: {call.excinfo.typename}: {call.excinfo.value}")
        else:
            logger.info(f"PASSED: {item.nodeid}")
```

**What each hook does:**

| Hook | When it runs | What to log |
|------|-------------|-------------|
| `pytest_runtest_setup` | Before each test | Test name (so you can find it in the log) |
| `pytest_runtest_teardown` | After each test | End marker |
| `pytest_runtest_makereport` | After each test phase | PASSED or FAILED with error details |

### Step 27 — Verify logging works

Run your tests with `-s` to see console logs:

```bash
pytest -v -s
```

You should see output like:

```
2026-09-03 12:00:01 INFO  [test_runner] ============================================================
2026-09-03 12:00:01 INFO  [test_runner] START: tests/test_auth.py::TestRegister::test_register_success
2026-09-03 12:00:01 INFO  [test_runner] ============================================================
2026-09-03 12:00:01 INFO  [api_client] REQUEST  POST http://localhost:8000/auth/register
2026-09-03 12:00:01 INFO  [api_client] RESPONSE 201 (45ms)
2026-09-03 12:00:01 INFO  [test_runner] PASSED: tests/test_auth.py::TestRegister::test_register_success
```

And check that a log file was created:

```bash
ls reports/logs/
cat reports/logs/test_run_*.log
```

The log file will have even more detail (DEBUG level) including request payloads and response bodies.

---

## PHASE 12: CI/CD Integration

### Step 28 — Create `.github/workflows/tests.yml`

Create the directories first:

```bash
mkdir -p .github/workflows
```

Then create the workflow file with these contents:

```yaml
name: API Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        working-directory: api_automation
        run: |
          python -m venv venv
          venv/bin/pip install -r requirements.txt

      - name: Start the service
        working-directory: .
        run: |
          venv/bin/pip install -r requirements.txt
          venv/bin/uvicorn app.main:app &
          sleep 5

      - name: Run tests
        working-directory: api_automation
        run: |
          venv/bin/pytest \
            --tb=short \
            -v \
            --html=reports/report.html \
            --self-contained-html \
            --junitxml=reports/results.xml

      - name: Upload test reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-reports
          path: |
            api_automation/reports/report.html
            api_automation/reports/results.xml
            api_automation/reports/logs/

      - name: Upload test results to GitHub
        if: always()
        uses: dorny/test-reporter@v1
        with:
          name: Test Results
          path: api_automation/reports/results.xml
          reporter: java-junit
```

**Key things to understand:**

| Part | Why |
|------|-----|
| `--junitxml=reports/results.xml` | Creates an XML report that CI tools (GitHub, Jenkins, GitLab) can parse to show test results in the UI |
| `--html=reports/report.html` | Human-readable HTML report |
| `if: always()` | Upload reports even when tests fail — this is critical, otherwise you lose the failure logs |
| `upload-artifact` | Makes reports downloadable from the GitHub Actions run page |
| `dorny/test-reporter` | Shows pass/fail results directly in the PR checks tab |

### Step 29 — Understand the JUnit XML report

The `--junitxml` flag creates an XML file that looks like:

```xml
<testsuite tests="31" failures="2" errors="0">
  <testcase classname="tests.test_auth.TestLogin" name="test_login_success" time="0.045"/>
  <testcase classname="tests.test_auth.TestLogin" name="test_login_wrong_password" time="0.032">
    <failure message="AssertionError: Expected 401, got 500. Body: ...">
      ... full traceback ...
    </failure>
  </testcase>
</testsuite>
```

CI tools parse this to show:
- Total tests, passed, failed
- Which specific tests failed
- The error message and traceback for each failure
- How long each test took

### Step 30 — Update `pytest.ini` for CI/CD

Add the JUnit XML output to your default options:

```ini
[pytest]
testpaths = tests
addopts = --tb=short -v --junitxml=reports/results.xml
markers =
    smoke: quick health check
    auth: authentication tests
    users: user CRUD tests
    products: product CRUD tests
    negative: error and edge case tests
```

Now every `pytest` run (local or CI) automatically produces the XML report.

---

## PHASE 13: Troubleshooting Failed Tests in CI/CD

### Step 31 — What to do when a test fails in CI

When a CI run fails, here is your troubleshooting checklist:

**1. Check the GitHub Actions log**
- Go to the Actions tab → click the failed run → click the "Run tests" step
- You'll see the pytest output with PASSED/FAILED for each test

**2. Download the test reports artifact**
- On the same page, scroll to "Artifacts" at the bottom
- Download `test-reports`
- Open `report.html` in a browser — it shows each test with pass/fail, duration, and error details
- Open the log files in `logs/` — they show every HTTP request and response

**3. Read the log file for the failed test**
- Search for `FAILED:` in the log file — it shows the test name
- Scroll up from there to see the REQUEST and RESPONSE that caused the failure
- The response body usually tells you exactly what went wrong

**Example log for a failure:**

```
2026-09-03 12:00:05 INFO  [test_runner] START: tests/test_auth.py::TestRegister::test_register_success
2026-09-03 12:00:05 INFO  [api_client] REQUEST  POST http://localhost:8000/auth/register
2026-09-03 12:00:05 DEBUG [api_client]   Payload: {'username': 'user_a3f2c1b9', 'email': 'user_a3f2c1b9@test.com', 'password': 'TestPass1234'}
2026-09-03 12:00:05 INFO  [api_client] RESPONSE 500 (120ms)
2026-09-03 12:00:05 DEBUG [api_client]   Body: {"detail":"Internal Server Error"}
2026-09-03 12:00:05 ERROR [test_runner] FAILED: tests/test_auth.py::TestRegister::test_register_success
2026-09-03 12:00:05 ERROR [test_runner]   Error: AssertionError: Expected 201, got 500. Body: {"detail":"Internal Server Error"}
```

From this you can see: the register endpoint returned 500, and the response body says "Internal Server Error" — so the problem is in the service, not the test.

---

## Updated Final Structure

```
api_automation/
├── .github/
│   └── workflows/
│       └── tests.yml                ← Step 28
├── config/
│   ├── __init__.py
│   └── settings.py                  ← Step 4
├── core/
│   ├── __init__.py
│   └── api_client.py                ← Step 7 + Step 25 (add logging)
├── utils/
│   ├── __init__.py
│   ├── test_data.py                 ← Step 5
│   ├── assertions.py                ← Step 6
│   └── logger.py                    ← Step 24
├── schemas/
│   ├── __init__.py
│   └── validators.py                ← Step 8
├── fixtures/
│   ├── __init__.py
│   ├── auth_fixtures.py             ← Step 9
│   └── data_fixtures.py             ← Step 10
├── tests/
│   ├── __init__.py
│   ├── test_health.py               ← Step 13
│   ├── test_auth.py                 ← Step 14
│   ├── test_users.py                ← Step 15
│   ├── test_products.py             ← Step 16
│   └── test_negative.py             ← Step 17
├── reports/                         (auto-created at runtime)
│   ├── logs/                        ← timestamped .log files
│   ├── results.xml                  ← JUnit XML for CI
│   └── report.html                  ← HTML report
├── conftest.py                      ← Step 11 + Step 26 (add logging hooks)
├── pytest.ini                       ← Step 12 + Step 22 + Step 30
├── requirements.txt                 ← Step 3 + Step 23
└── venv/
```

---

## Updated Quick Reference

| Command | What It Does |
|---------|-------------|
| `pytest -v -s` | Run all tests, show logs in console |
| `pytest -m smoke -v` | Run only smoke tests |
| `pytest --tb=long -v` | Run with full tracebacks (deep debugging) |
| `pytest --tb=line -v` | Run with one-line failure summaries |
| `pytest --html=reports/report.html --self-contained-html` | Generate HTML report |
| `pytest --junitxml=reports/results.xml` | Generate JUnit XML for CI |
| `cat reports/logs/test_run_*.log` | Read the detailed log file |
| `grep "FAILED" reports/logs/test_run_*.log` | Find all failures in the log |
| `grep -B 10 "FAILED" reports/logs/test_run_*.log` | See 10 lines before each failure (shows the request/response that caused it) |
