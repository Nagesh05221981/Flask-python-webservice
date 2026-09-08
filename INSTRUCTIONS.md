# QA Automation Framework — Build Instructions

Build a complete API test framework for the FastAPI service from scratch.

---

## PHASE 1: Setup

### Step 1 — Create project folder

```bash
cd /Users/nageshallur/my-service
mkdir -p qa_framework
cd qa_framework
```

### Step 2 — Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Create requirements.txt

```
pytest
requests
pytest-html
jsonschema
```

Install:

```bash
pip install -r requirements.txt
```

### Step 4 — Create the full folder structure

```bash
mkdir -p config
mkdir -p core
mkdir -p schemas
mkdir -p fixtures
mkdir -p utils
mkdir -p tests
mkdir -p reports

touch config/__init__.py
touch core/__init__.py
touch schemas/__init__.py
touch fixtures/__init__.py
touch utils/__init__.py
touch tests/__init__.py
```

Your structure should look like:

```
qa_framework/
├── requirements.txt
├── pytest.ini
├── conftest.py
├── config/
│   ├── __init__.py
│   └── settings.py
├── core/
│   ├── __init__.py
│   └── api_client.py
├── schemas/
│   ├── __init__.py
│   └── validators.py
├── fixtures/
│   ├── __init__.py
│   ├── auth_fixtures.py
│   └── data_fixtures.py
├── utils/
│   ├── __init__.py
│   ├── assertions.py
│   └── test_data.py
├── tests/
│   ├── __init__.py
│   ├── test_health.py
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_products.py
│   └── test_negative.py
└── reports/
```

---

## PHASE 2: Config & Utilities

### Step 5 — Create config/settings.py

This lets you run tests against different environments.

```python
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
TEST_USER = os.getenv("TEST_USER", "testuser")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "TestPass123")
TEST_EMAIL = os.getenv("TEST_EMAIL", "testuser@example.com")
```

### Step 6 — Create utils/test_data.py

Generates random test data so tests don't clash with each other.

```python
import uuid


def generate_user():
    unique = uuid.uuid4().hex[:8]
    return {
        "username": f"user_{unique}",
        "email": f"user_{unique}@test.com",
        "password": "TestPass123"
    }


def generate_product():
    unique = uuid.uuid4().hex[:8]
    return {
        "name": f"Product_{unique}",
        "description": f"Test product {unique}",
        "price": 19.99,
        "in_stock": True
    }
```

### Step 7 — Create utils/assertions.py

Reusable assertion helpers with clear error messages.

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

---

## PHASE 3: Core API Client

### Step 8 — Create core/api_client.py

A wrapper around `requests` so you don't repeat BASE_URL and headers everywhere.

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

    def register(self, payload):
        return self.session.post(f"{self.base_url}/auth/register", json=payload)

    def login(self, username, password):
        return self.session.post(
            f"{self.base_url}/auth/login",
            data={"username": username, "password": password}
        )

    def get_me(self):
        return self.session.get(f"{self.base_url}/auth/me")

    def list_users(self, skip=0, limit=20):
        return self.session.get(
            f"{self.base_url}/users/",
            params={"skip": skip, "limit": limit}
        )

    def get_user(self, user_id):
        return self.session.get(f"{self.base_url}/users/{user_id}")

    def update_user(self, user_id, payload):
        return self.session.put(f"{self.base_url}/users/{user_id}", json=payload)

    def delete_user(self, user_id):
        return self.session.delete(f"{self.base_url}/users/{user_id}")

    def create_product(self, payload):
        return self.session.post(f"{self.base_url}/products/", json=payload)

    def list_products(self, skip=0, limit=20):
        return self.session.get(
            f"{self.base_url}/products/",
            params={"skip": skip, "limit": limit}
        )

    def get_product(self, product_id):
        return self.session.get(f"{self.base_url}/products/{product_id}")

    def update_product(self, product_id, payload):
        return self.session.put(
            f"{self.base_url}/products/{product_id}", json=payload
        )

    def delete_product(self, product_id):
        return self.session.delete(f"{self.base_url}/products/{product_id}")

    def health_check(self):
        return self.session.get(f"{self.base_url}/")
```

---

## PHASE 4: Schema Validators

### Step 9 — Create schemas/validators.py

Validates response JSON has the correct shape.

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

---

## PHASE 5: Fixtures

### Step 10 — Create fixtures/auth_fixtures.py

Shared fixtures for authentication.

```python
import pytest
from core.api_client import ApiClient
from utils.test_data import generate_user


@pytest.fixture
def client():
    """Return a fresh ApiClient instance."""
    return ApiClient()


@pytest.fixture
def registered_user(client):
    """Register a new user, return dict with user data + password."""
    user_data = generate_user()
    response = client.register(user_data)
    assert response.status_code == 201
    result = response.json()
    result["password"] = user_data["password"]
    return result


@pytest.fixture
def authenticated_client(client, registered_user):
    """Return an ApiClient that is logged in."""
    response = client.login(registered_user["username"], registered_user["password"])
    assert response.status_code == 200
    token = response.json()["access_token"]
    client.set_token(token)
    return client
```

### Step 11 — Create fixtures/data_fixtures.py

Fixtures that create seed data (products).

```python
import pytest
from utils.test_data import generate_product


@pytest.fixture
def created_product(authenticated_client):
    """Create a product and return its data."""
    product_data = generate_product()
    response = authenticated_client.create_product(product_data)
    assert response.status_code == 201
    return response.json()
```

### Step 12 — Create conftest.py (at project root)

Import all fixtures so they're available to all tests.

```python
from fixtures.auth_fixtures import *
from fixtures.data_fixtures import *
```

---

## PHASE 6: Pytest Config

### Step 13 — Create pytest.ini

```ini
[pytest]
testpaths = tests
markers =
    smoke: quick health checks
    auth: authentication tests
    users: user CRUD tests
    products: product CRUD tests
    negative: error and edge case tests
```

---

## PHASE 7: Test Files

### Step 14 — Create tests/test_health.py

```python
import pytest
from utils.assertions import assert_status


@pytest.mark.smoke
def test_health_check(client):
    response = client.health_check()
    assert_status(response, 200)
```

### Step 15 — Create tests/test_auth.py

```python
import pytest
from utils.assertions import assert_status, assert_json_has_keys, assert_error
from utils.test_data import generate_user
from schemas.validators import is_valid_user, is_valid_token


@pytest.mark.auth
class TestRegister:

    def test_register_success(self, client):
        user = generate_user()
        response = client.register(user)
        assert_status(response, 201)
        assert is_valid_user(response.json())

    def test_register_duplicate_username(self, client, registered_user):
        duplicate = {
            "username": registered_user["username"],
            "email": "other@test.com",
            "password": "TestPass123"
        }
        response = client.register(duplicate)
        assert_status(response, 400)

    def test_register_duplicate_email(self, client, registered_user):
        duplicate = {
            "username": "someone_else",
            "email": registered_user["email"],
            "password": "TestPass123"
        }
        response = client.register(duplicate)
        assert_status(response, 400)


@pytest.mark.auth
class TestLogin:

    def test_login_success(self, client, registered_user):
        response = client.login(registered_user["username"], registered_user["password"])
        assert_status(response, 200)
        assert is_valid_token(response.json())

    def test_login_wrong_password(self, client, registered_user):
        response = client.login(registered_user["username"], "WrongPass999")
        assert_status(response, 401)

    def test_login_nonexistent_user(self, client):
        response = client.login("nouser_xyz", "nopass")
        assert_status(response, 401)


@pytest.mark.auth
class TestMe:

    def test_get_me(self, authenticated_client, registered_user):
        response = authenticated_client.get_me()
        assert_status(response, 200)
        assert response.json()["username"] == registered_user["username"]

    def test_get_me_no_auth(self, client):
        response = client.get_me()
        assert_status(response, 401)
```

### Step 16 — Create tests/test_users.py

```python
import pytest
from utils.assertions import assert_status, assert_error
from utils.test_data import generate_user
from schemas.validators import is_valid_user


@pytest.mark.users
class TestListUsers:

    def test_list_users(self, authenticated_client):
        response = authenticated_client.list_users()
        assert_status(response, 200)
        assert isinstance(response.json(), list)

    def test_list_users_no_auth(self, client):
        response = client.list_users()
        assert_status(response, 401)


@pytest.mark.users
class TestGetUser:

    def test_get_user_by_id(self, authenticated_client, registered_user):
        user_id = registered_user["id"]
        response = authenticated_client.get_user(user_id)
        assert_status(response, 200)
        assert is_valid_user(response.json())

    def test_get_user_not_found(self, authenticated_client):
        response = authenticated_client.get_user(99999)
        assert_status(response, 404)


@pytest.mark.users
class TestUpdateUser:

    def test_update_own_email(self, authenticated_client, registered_user):
        user_id = registered_user["id"]
        response = authenticated_client.update_user(user_id, {"email": "new@test.com"})
        assert_status(response, 200)
        assert response.json()["email"] == "new@test.com"

    def test_update_other_user_forbidden(self, authenticated_client):
        """Try to update user_id=1 (not ours) — should get 403."""
        response = authenticated_client.update_user(1, {"email": "hack@test.com"})
        assert response.status_code in [403, 404]


@pytest.mark.users
class TestDeleteUser:

    def test_delete_own_account(self, client):
        """Register, login, delete self."""
        user_data = generate_user()
        reg = client.register(user_data)
        assert_status(reg, 201)
        user_id = reg.json()["id"]

        login = client.login(user_data["username"], user_data["password"])
        client.set_token(login.json()["access_token"])

        response = client.delete_user(user_id)
        assert_status(response, 204)

    def test_delete_other_user_forbidden(self, authenticated_client):
        response = authenticated_client.delete_user(1)
        assert response.status_code in [403, 404]
```

### Step 17 — Create tests/test_products.py

```python
import pytest
from utils.assertions import assert_status
from utils.test_data import generate_product
from schemas.validators import is_valid_product


@pytest.mark.products
class TestCreateProduct:

    def test_create_product(self, authenticated_client):
        product = generate_product()
        response = authenticated_client.create_product(product)
        assert_status(response, 201)
        assert is_valid_product(response.json())

    def test_create_product_no_auth(self, client):
        product = generate_product()
        response = client.create_product(product)
        assert_status(response, 401)


@pytest.mark.products
class TestListProducts:

    def test_list_products(self, authenticated_client):
        response = authenticated_client.list_products()
        assert_status(response, 200)
        assert isinstance(response.json(), list)


@pytest.mark.products
class TestGetProduct:

    def test_get_product_by_id(self, authenticated_client, created_product):
        product_id = created_product["id"]
        response = authenticated_client.get_product(product_id)
        assert_status(response, 200)
        assert is_valid_product(response.json())

    def test_get_product_not_found(self, authenticated_client):
        response = authenticated_client.get_product(99999)
        assert_status(response, 404)


@pytest.mark.products
class TestUpdateProduct:

    def test_update_own_product(self, authenticated_client, created_product):
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
        product_id = created_product["id"]
        response = authenticated_client.delete_product(product_id)
        assert_status(response, 204)

        # Verify it's gone
        response = authenticated_client.get_product(product_id)
        assert_status(response, 404)
```

### Step 18 — Create tests/test_negative.py

```python
import pytest
from utils.assertions import assert_status, assert_error


@pytest.mark.negative
class TestAuthNegative:

    def test_register_missing_fields(self, client):
        response = client.register({"username": "onlyname"})
        assert response.status_code == 422

    def test_register_invalid_email(self, client):
        response = client.register({
            "username": "baduser",
            "email": "not-an-email",
            "password": "TestPass123"
        })
        assert response.status_code == 422

    def test_login_empty_credentials(self, client):
        response = client.login("", "")
        assert response.status_code in [401, 422]


@pytest.mark.negative
class TestProductsNegative:

    def test_create_product_missing_name(self, authenticated_client):
        response = authenticated_client.create_product({"price": 10.0})
        assert response.status_code == 422

    def test_create_product_missing_price(self, authenticated_client):
        response = authenticated_client.create_product({"name": "No Price"})
        assert response.status_code == 422

    def test_create_product_negative_price(self, authenticated_client):
        response = authenticated_client.create_product({
            "name": "Bad",
            "price": -5.0
        })
        # Depends on your API validation — may be 422 or 201
        # Update this assertion based on your API behavior
        assert response.status_code in [201, 422]


@pytest.mark.negative
class TestUnauthorized:

    def test_list_users_no_auth(self, client):
        response = client.list_users()
        assert_status(response, 401)

    def test_create_product_no_auth(self, client):
        response = client.create_product({"name": "X", "price": 1.0})
        assert_status(response, 401)

    def test_get_me_no_auth(self, client):
        response = client.get_me()
        assert_status(response, 401)

    def test_delete_user_no_auth(self, client):
        response = client.delete_user(1)
        assert_status(response, 401)
```

---

## PHASE 8: Run Tests

### Step 19 — Start your service (separate terminal)

```bash
cd /Users/nageshallur/my-service
uvicorn app.main:app --reload
```

### Step 20 — Run all tests

```bash
cd /Users/nageshallur/my-service/qa_framework
source venv/bin/activate
pytest -v
```

### Step 21 — Run by category

```bash
# Only smoke tests
pytest -m smoke -v

# Only auth tests
pytest -m auth -v

# Only product tests
pytest -m products -v

# Only negative tests
pytest -m negative -v
```

### Step 22 — Generate HTML report

```bash
pytest -v --html=reports/report.html --self-contained-html
```

Open `reports/report.html` in a browser.

---

## PHASE 9: Verify Checklist

After all steps, run `pytest -v` and confirm:

| Test File           | Expected Tests | What It Covers                        |
|---------------------|----------------|---------------------------------------|
| test_health.py      | 1              | Health check endpoint                 |
| test_auth.py        | 8              | Register, login, /me, duplicates      |
| test_users.py       | 7              | List, get, update, delete users       |
| test_products.py    | 6              | Create, list, get, update, delete     |
| test_negative.py    | 9              | Missing fields, bad data, no auth     |
| **Total**           | **31**         |                                       |

---

## Quick Reference

| Command                              | What It Does                  |
|---------------------------------------|-------------------------------|
| `pytest -v`                           | Run all tests, verbose        |
| `pytest -m smoke -v`                  | Run only smoke tests          |
| `pytest tests/test_auth.py -v`        | Run one file                  |
| `pytest -k "test_login" -v`          | Run tests matching a keyword  |
| `pytest -v -s`                        | Show print() output           |
| `pytest --html=reports/report.html`   | Generate HTML report          |
| `BASE_URL=http://staging:8000 pytest` | Run against another env       |

---

## PHASE 10: Logging & Allure Reporting

### Step 23 — Update requirements.txt

Add these two lines to `requirements.txt`:

```
allure-pytest
```

Then install:

```bash
cd /Users/nageshallur/my-service/qa_framework
source venv/bin/activate
pip install -r requirements.txt
```

### Step 24 — Install Allure CLI

```bash
brew install allure
```

Verify it installed:

```bash
allure --version
```

### Step 25 — Create utils/logger.py

This creates a centralized logger that writes to both the console and a log file.

```python
import logging
import os
from datetime import datetime


def get_logger(name):
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Create reports/logs directory
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports", "logs")
    os.makedirs(log_dir, exist_ok=True)

    # Log file named by date
    log_file = os.path.join(log_dir, f"test_run_{datetime.now().strftime('%Y%m%d')}.log")

    # File handler — DEBUG level (captures everything)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    # Console handler — INFO level (cleaner output)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Format
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-5s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
```

### Step 26 — Add logging to core/api_client.py

Add request/response logging to every API call. Replace your entire `api_client.py` with:

```python
import time
import requests
from config.settings import BASE_URL
from utils.logger import get_logger

logger = get_logger("api_client")


class ApiClient:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.token = None

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

    def set_token(self, token):
        self.token = token
        self.session.headers["Authorization"] = f"Bearer {token}"
        logger.info("Auth token set")

    def clear_auth(self):
        self.token = None
        self.session.headers.pop("Authorization", None)
        logger.info("Auth cleared")

    def register(self, payload):
        return self._request("POST", "/auth/register", json=payload)

    def login(self, username, password):
        return self._request("POST", "/auth/login", data={"username": username, "password": password})

    def get_me(self):
        return self._request("GET", "/auth/me")

    def list_users(self, skip=0, limit=20):
        return self._request("GET", "/users/", params={"skip": skip, "limit": limit})

    def get_user(self, user_id):
        return self._request("GET", f"/users/{user_id}")

    def update_user(self, user_id, payload):
        return self._request("PUT", f"/users/{user_id}", json=payload)

    def delete_user(self, user_id):
        return self._request("DELETE", f"/users/{user_id}")

    def create_product(self, payload):
        return self._request("POST", "/products/", json=payload)

    def list_products(self, skip=0, limit=20):
        return self._request("GET", "/products/", params={"skip": skip, "limit": limit})

    def get_product(self, product_id):
        return self._request("GET", f"/products/{product_id}")

    def update_product(self, product_id, payload):
        return self._request("PUT", f"/products/{product_id}", json=payload)

    def delete_product(self, product_id):
        return self._request("DELETE", f"/products/{product_id}")

    def health_check(self):
        return self._request("GET", "/")
```

**What changed:** All methods now go through `_request()` which logs every request and response with timing. The individual methods are now one-liners.

### Step 27 — Add Allure and logging hooks to conftest.py

Replace your `conftest.py` with:

```python
import allure
from utils.logger import get_logger
from fixtures.auth_fixtures import *
from fixtures.data_fixtures import *

logger = get_logger("test_runner")


@allure.title("{item.name}")
def pytest_runtest_setup(item):
    logger.info(f"--- START: {item.nodeid} ---")


def pytest_runtest_teardown(item):
    logger.info(f"--- END: {item.nodeid} ---")


def pytest_runtest_makereport(item, call):
    if call.when == "call":
        if call.excinfo is not None:
            logger.error(f"FAILED: {item.nodeid} — {call.excinfo.typename}: {call.excinfo.value}")
        else:
            logger.info(f"PASSED: {item.nodeid}")
```

**What this does:**
- Logs the start and end of every test
- Logs PASSED/FAILED with error details on failure
- Integrates with Allure for report generation

### Step 28 — Add Allure decorators to test files

Add Allure decorators to your existing tests for richer reports. Here is the pattern — apply it to each test file:

**tests/test_health.py:**

```python
import pytest
import allure
from utils.assertions import assert_status


@allure.feature("Health")
@pytest.mark.smoke
def test_healthcheck(client):
    with allure.step("Call health check endpoint"):
        response = client.health_check()
    with allure.step("Verify status 200"):
        assert_status(response, 200)
```

**tests/test_auth.py — add these decorators to the class/methods:**

```python
import pytest
import allure
from utils.assertions import assert_status, assert_json_has_keys, assert_error
from utils.test_data import generate_user
from schemas.validators import is_valid_user, is_valid_token


@allure.feature("Authentication")
@pytest.mark.auth
class TestRegister:

    @allure.story("Register")
    def test_register_success(self, client):
        with allure.step("Generate user data"):
            user = generate_user()
        with allure.step("Register user"):
            response = client.register(user)
        with allure.step("Verify 201 and valid user response"):
            assert_status(response, 201)
            assert is_valid_user(response.json())
```

**The pattern for all tests is:**
1. Add `@allure.feature("FeatureName")` on the class
2. Add `@allure.story("StoryName")` on each method
3. Wrap logical steps with `with allure.step("description"):`

Apply this same pattern to `test_users.py`, `test_products.py`, and `test_negative.py` as you create them.

### Step 29 — Update pytest.ini

Add Allure results directory:

```ini
[pytest]
testpaths = tests
addopts = --alluredir=reports/allure-results
markers =
    smoke: quick health checks
    auth: authentication tests
    users: user CRUD tests
    products: product CRUD tests
    negative: error and edge case tests
```

### Step 30 — Run tests and generate Allure report

**Run tests (results are saved automatically):**

```bash
cd /Users/nageshallur/my-service/qa_framework
source venv/bin/activate
pytest -v -s
```

**Generate and open the Allure report:**

```bash
allure serve reports/allure-results
```

This opens a browser with the full interactive report.

**To generate a static HTML report instead:**

```bash
allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report
```

### Step 31 — Verify everything works

After completing all steps, confirm:

| What | Where |
|------|-------|
| Console logs | Visible in terminal when running `pytest -v -s` |
| Log file | `reports/logs/test_run_YYYYMMDD.log` |
| Allure raw data | `reports/allure-results/` |
| Allure HTML report | Opens in browser via `allure serve` |

Your log file should show entries like:

```
2026-07-07 10:15:03 INFO  [test_runner] --- START: tests/test_auth.py::TestRegister::test_register_success ---
2026-07-07 10:15:03 INFO  [api_client] REQUEST  POST http://localhost:8000/auth/register
2026-07-07 10:15:03 DEBUG [api_client]   Payload: {'username': 'user_a3bc...', ...}
2026-07-07 10:15:03 INFO  [api_client] RESPONSE 201 (45ms)
2026-07-07 10:15:03 INFO  [test_runner] PASSED: tests/test_auth.py::TestRegister::test_register_success
2026-07-07 10:15:03 INFO  [test_runner] --- END: tests/test_auth.py::TestRegister::test_register_success ---
```

---

## Updated Folder Structure

```
qa_framework/
├── requirements.txt          (updated — added allure-pytest)
├── pytest.ini                (updated — added addopts)
├── conftest.py               (updated — added logging + allure hooks)
├── config/
│   ├── __init__.py
│   └── settings.py
├── core/
│   ├── __init__.py
│   └── api_client.py         (updated — added request/response logging)
├── schemas/
│   ├── __init__.py
│   └── validators.py
├── fixtures/
│   ├── __init__.py
│   ├── auth_fixtures.py
│   └── data_fixtures.py
├── utils/
│   ├── __init__.py
│   ├── assertions.py
│   ├── test_data.py
│   └── logger.py             (NEW)
├── tests/
│   ├── __init__.py
│   ├── test_health.py        (updated — added allure decorators)
│   ├── test_auth.py          (updated — added allure decorators)
│   ├── test_users.py
│   ├── test_products.py
│   └── test_negative.py
└── reports/
    ├── logs/                  (auto-created)
    ├── allure-results/        (auto-created)
    └── allure-report/         (generated)
```

---

## Quick Reference (updated)

| Command | What It Does |
|---------|-------------|
| `pytest -v -s` | Run all tests with logs visible |
| `pytest -v -s -m smoke` | Run smoke tests with logs |
| `allure serve reports/allure-results` | Open live Allure report |
| `allure generate reports/allure-results -o reports/allure-report --clean` | Generate static report |
