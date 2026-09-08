import pytest
from core.api_client import ApiClient
from utils.test_data import generate_user

@pytest.fixture
def client():
    """ REturn a fresh ApiClient"""
    return ApiClient()

@pytest.fixture
def registered_user(client):
    """Register a new user and retutn dict with user data and password"""
    user_data =generate_user()
    response = client.register(user_data)
    assert response.status_code == 201
    result = response.json()
    result["password"] = user_data["password"]
    return result

@pytest.fixture
def authenticated_client(client,registered_user):
    """Return an apiclient that is registered"""
    response =client.login(registered_user["username"],registered_user["password"])
    assert response.status_code == 200
    token = response.json()["access_token"]
    client.set_token(token)
    return client


