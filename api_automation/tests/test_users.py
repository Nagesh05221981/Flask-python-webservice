import uuid
import pytest
import allure
from utils.assertions import assert_status, assert_error
from utils.test_data import generate_user
from schemas.validators import validate_user, validate_user_list


@allure.feature("Users")
@pytest.mark.users
class TestListUsers:

    def test_list_users(self, authenticated_client):
        """List all users — expect 200 and a list."""
        response = authenticated_client.list_users()
        assert_status(response, 200)
        validate_user_list(response.json())

    def test_list_users_no_auth(self, client):
        """List users without token — expect 401."""
        response = client.list_users()
        assert_status(response, 401)


@allure.feature("Users")
@pytest.mark.users
class TestGetUser:

    def test_get_user_by_id(self, authenticated_client, registered_user):
        """Get a user by ID — expect 200 and valid user object."""
        user_id = registered_user["id"]
        response = authenticated_client.get_user(user_id)
        assert_status(response, 200)
        validate_user(response.json())

    def test_get_user_not_found(self, authenticated_client):
        """Get a user that doesn't exist — expect 404."""
        response = authenticated_client.get_user(99999)
        assert_status(response, 404)


@allure.feature("Users")
@pytest.mark.users
class TestUpdateUser:

    def test_update_own_email(self, authenticated_client, registered_user):
        """Update your own email — expect 200 and updated value."""
        user_id = registered_user["id"]
        new_email = f"updated_{uuid.uuid4().hex[:8]}@test.com"
        response = authenticated_client.update_user(user_id, {"email": new_email})
        assert_status(response, 200)
        assert response.json()["email"] == new_email

    def test_update_other_user_forbidden(self, authenticated_client):
        """Try to update another user's account — expect 403 or 404."""
        response = authenticated_client.update_user(1, {"email": "hack@test.com"})
        assert response.status_code in [403, 404]


@allure.feature("Users")
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
