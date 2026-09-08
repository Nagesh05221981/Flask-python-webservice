import pytest
import allure
from utils.assertions import assert_status,assert_error,assert_json_has_keys
from utils.test_data import generate_user
from schemas.validators import validate_user, validate_token


@allure.feature("Authentication")
@pytest.mark.auth
class TestRegister:

    @allure.story("Register")
    def test_register(self,client):
        with allure.step("Generate user data"):
            user = generate_user()
        with allure.step("Register user"):
            response = client.register(user)
        with allure.step("Verify 201 and valid user response"):
            assert_status(response,201)
            validate_user(response.json())

    @allure.story("Register")
    def test_duplicate_username(self,client,registered_user):
        """Register with an already-taken username — expect 400."""
        with allure.step("Register with duplicate username"):
            duplicate = {
                "username":registered_user["username"],
                "email": "other@test.com",
                "password": "TestPass123",
            }
            response = client.register(duplicate)
        with allure.step("Verify 400"):
            assert_status(response, 400)

    @allure.story("Register")
    def test_duplicate_email(self,client,registered_user):
        """Register with an already-taken email — expect 400."""
        with allure.step("Register with duplicate email"):
            duplicate = {
                "username": "someone_else",
                "email": registered_user["email"],
                "password": "TestPass123",
            }
            response = client.register(duplicate)
        with allure.step("Verify 400"):
            assert_status(response, 400)


@allure.feature("Authentication")
@pytest.mark.auth
class TestLogin:

    @allure.story("Login")
    def test_login_success(self,client,registered_user):
        """Login with valid credentials — expect 200 and token."""
        with allure.step("Login with valid credentials"):
            response = client.login(registered_user["username"],registered_user["password"])
        with allure.step("Verify 200 and valid token"):
            assert_status(response,200)
            validate_token(response.json())

    @allure.story("Login")
    def test_login_wrong_password(self, client, registered_user):
        """Login with wrong password — expect 401."""
        with allure.step("Login with wrong password"):
            response = client.login(registered_user["username"], "WrongPass999")
        with allure.step("Verify 401"):
            assert_status(response, 401)

    @allure.story("Login")
    def test_login_nonexistent_user(self,client):
        """Login with a user that doesn't exist — expect 401."""
        with allure.step("Login with nonexistent user"):
            response = client.login("nouser_xyz","nopass")
        with allure.step("Verify 401"):
            assert_status(response,401)


@allure.feature("Authentication")
@pytest.mark.auth
class TestMe:

    @allure.story("Me")
    def test_get_me(self,authenticated_client,registered_user):
        """Get current user profile — expect 200 and correct username."""
        with allure.step("Call /auth/me"):
            response = authenticated_client.get_me()
        with allure.step("Verify 200 and correct username"):
            assert_status(response,200)
            assert response.json()["username"] == registered_user["username"]

    @allure.story("Me")
    def test_get_me_no_auth(self,client):
        """Get /auth/me without token — expect 401."""
        with allure.step("Call /auth/me without token"):
            response = client.get_me()
        with allure.step("Verify 401"):
            assert_status(response,401)
