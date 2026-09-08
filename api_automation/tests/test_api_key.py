import pytest
import allure
from utils.assertions import assert_status
from schemas.validators import validate_user, validate_product, validate_user_list


@allure.feature("API Key Authentication")
@pytest.mark.auth
class TestApiKeyAuth:

    def test_get_me_with_api_key(self, api_key_client, registered_user):
        """Access /auth/me using API key — expect 200 and correct username."""
        response = api_key_client.get_me()
        assert_status(response, 200)
        assert response.json()["username"] == registered_user["username"]

    def test_list_users_with_api_key(self, api_key_client):
        """List users using API key — expect 200."""
        response = api_key_client.list_users()
        assert_status(response, 200)
        validate_user_list(response.json())

    def test_create_product_with_api_key(self, api_key_client):
        """Create a product using API key — expect 201."""
        product = {"name": "API Key Product", "price": 25.0, "description": "test", "in_stock": True}
        response = api_key_client.create_product(product)
        assert_status(response, 201)
        validate_product(response.json())

    def test_invalid_api_key(self, client):
        """Use a fake API key — expect 401."""
        client.set_api_key("fake-invalid-key-12345")
        response = client.get_me()
        assert_status(response, 401)
