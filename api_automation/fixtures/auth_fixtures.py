import pytest
from core.api_client import ApiClient
from utils.test_data import generate_user


@pytest.fixture
def client():
    return ApiClient()

@pytest.fixture
def registered_user(client):
    user_data = generate_user()
    response = client.register(user_data)
    assert  response.status_code == 201
    result = response.json()
    # keep the password so that we can use it
    result["password"] = user_data["password"]
    return result


@pytest.fixture
def authenticated_client(client,registered_user):
    """
    return an apiClient that is logged in
    using a bearer token
    """
    response = client.login(registered_user["username"], registered_user["password"])
    assert response.status_code == 200
    token = response.json()["access_token"]
    client.set_token(token)
    return client


@pytest.fixture
def api_key_client(client,registered_user):
    """Return an ApiClient authenticated via X-API-Key header."""
    api_key = registered_user["api_key"]
    client.set_api_key(api_key)
    return client


@pytest.fixture
def oauth_client(client):
    """Return an ApiClient authenticated via the dummy OAuth flow."""
    # Exchange the dummy code for a JWT token
    response = client.oauth_callback("dummy-auth-code-123")
    assert response.status_code == 200
    token = response.json()["access_token"]
    client.set_token(token)
    return client
