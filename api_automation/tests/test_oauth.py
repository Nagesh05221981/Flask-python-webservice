import pytest
import allure
from utils.assertions import assert_status
from schemas.validators import validate_token, validate_user, validate_user_list, validate_product


@allure.feature("OAuth Authentication")
@pytest.mark.auth
class TestOAuthLogin:

    def test_get_oauth_login_url(self, client):
        """GET /auth/oauth/login — expect 200 and an authorization URL."""
        response = client.oauth_login()
        assert_status(response, 200)
        data = response.json()
        assert "authorization_url" in data

    def test_oauth_callback_success(self, client):
        """Exchange valid dummy code for a token — expect 200 and valid token."""
        response = client.oauth_callback("dummy-auth-code-123")
        assert_status(response, 200)
        validate_token(response.json())

    def test_oauth_callback_invalid_code(self, client):
        """Exchange invalid code — expect 400."""
        response = client.oauth_callback("bad-code-999")
        assert_status(response, 400)


@allure.feature("OAuth Authentication")
@pytest.mark.auth
class TestOAuthAccess:

    def test_oauth_user_can_access_me(self, oauth_client):
        """OAuth-authenticated client can access /auth/me — expect 200."""
        response = oauth_client.get_me()
        assert_status(response, 200)
        validate_user(response.json())
        assert response.json()["username"] == "oauth_user"

    def test_oauth_user_can_list_users(self, oauth_client):
        """OAuth-authenticated client can list users — expect 200."""
        response = oauth_client.list_users()
        assert_status(response, 200)
        validate_user_list(response.json())

    def test_oauth_user_can_create_product(self, oauth_client):
        """OAuth-authenticated client can create products — expect 201."""
        product = {"name": "OAuth Product", "price": 15.0, "description": "test", "in_stock": True}
        response = oauth_client.create_product(product)
        assert_status(response, 201)
        validate_product(response.json())
