import pytest
import requests
from core.swagger_test_builder import TestBuilder
from config.settings import BASE_URL, TEST_USER
from schemas.validators import is_valid_user, is_valid_product, is_valid_token

builder = TestBuilder(
    spec_path="swagger/openapi.yaml",
    base_url=BASE_URL,
)


def _ensure_test_user():
    """Register a test user (ignore if already exists) and authenticate."""
    requests.post(
        BASE_URL + "/auth/register",
        json=TEST_USER,
    )
    builder.client.authenticate(TEST_USER["username"], TEST_USER["password"])


def _create_disposable_user():
    """Create a second user whose ID can be safely used for DELETE /users/{id}."""
    resp = requests.post(
        BASE_URL + "/auth/register",
        json={
            "username": "disposable_user",
            "email": "disposable@example.com",
            "password": "disposable123",
        },
    )
    if resp.status_code == 201:
        return resp.json()["id"]
    # Already exists — look up via the users list
    me_resp = builder.client.request("GET", "/users/")
    for user in me_resp.json():
        if user["username"] == "disposable_user":
            return user["id"]
    return None


_ensure_test_user()

# Seed a product so GET/PUT tests on /products/{id} have data
builder.client.request("POST", "/products/", json={
    "name": "Seed Product",
    "description": "Created for tests",
    "price": 5.00,
})

disposable_user_id = _create_disposable_user()

test_cases = builder.generate_tests()


DISPOSABLE_CREDS = {
    "username": "disposable_user",
    "password": "disposable123",
}


def _is_delete_user(method, path):
    return method == "DELETE" and path.startswith("/users/")


@pytest.mark.parametrize(
    "method,path,body,expected_status,content_type",
    test_cases,
    ids=[f"{m} {p}" for m, p, _, _, _ in test_cases],
)
def test_api_endpoints(method, path, body, expected_status, content_type):
    if _is_delete_user(method, path) and disposable_user_id:
        # Authenticate as the disposable user so they can delete themselves
        builder.client.authenticate(**DISPOSABLE_CREDS)
        path = f"/users/{disposable_user_id}"

    response = builder.client.request(method, path, json=body, content_type=content_type)

    if _is_delete_user(method, path):
        # Restore the main test user's auth
        builder.client.authenticate(TEST_USER["username"], TEST_USER["password"])

    # --- Fix 5: Assert exact expected status code ---
    assert response.status_code == expected_status, (
        f"{method} {path} returned {response.status_code}, expected {expected_status}. "
        f"Body: {response.text}"
    )

    # --- Fix 6: Validate response schemas where applicable ---
    if response.status_code == 204:
        return  # no body to validate

    data = response.json()

    if "/auth/login" in path or "/auth/oauth/callback" in path:
        ok, reason = is_valid_token(data)
        assert ok, reason

    elif "/auth/me" in path or ("/users/" in path and method == "GET"):
        if isinstance(data, list):
            for user in data:
                ok, reason = is_valid_user(user)
                assert ok, reason
        elif isinstance(data, dict) and "id" in data:
            ok, reason = is_valid_user(data)
            assert ok, reason

    elif "/products/" in path and method in ("GET", "POST", "PUT"):
        if isinstance(data, list):
            for product in data:
                ok, reason = is_valid_product(product)
                assert ok, reason
        elif isinstance(data, dict) and "id" in data:
            ok, reason = is_valid_product(data)
            assert ok, reason
