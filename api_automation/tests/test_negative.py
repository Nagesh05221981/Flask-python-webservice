import pytest
import allure
from utils.assertions import assert_status


@allure.feature("Negative Tests")
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


@allure.feature("Negative Tests")
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


@allure.feature("Negative Tests")
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
