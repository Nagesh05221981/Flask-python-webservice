import pytest
from utils.assertions import assert_status, assert_json_has_keys,assert_error
from utils.test_data import generate_user
from schemas.validators import is_valid_user , is_valid_token

@pytest.mark.auth
class TestRegister:
    def test_register_success(self,client):
        user = generate_user()
        response = client.register(user)
        assert_status(response,201)
        assert is_valid_user(response.json())

    def test_duplicate_user(self,client,registered_user):
        duplicate = {
            "username": registered_user["username"],
            "email": "other@test.com",
            "password": "TestPass123"

        }
        response = client.register(duplicate)
        assert_status(response,400)

@pytest.mark.auth
class TestLogin:
    def test_login_success(self,client,registered_user):
        response = client.login(registered_user["username"],registered_user["password"])
        assert_status(response,200)
        assert is_valid_token(response.json())

    def test_login_wrong_password(self,client,registered_user):
        response  = client.login(registered_user["username"],"sdfsdf")
        assert_status(response,401)

    def test_login_nonexistinguser(self,client):
        response = client.login("abcd","defgh")
        assert_status(response,401)

@pytest.mark.auth
class TestMe:
    def test_get_me(self,authenticated_client,registered_user):
        response = authenticated_client.get_me()
        assert_status(response,200)
        assert response.json()["username"] == registered_user["username"]

    def test_get_me_no_auth(self,client):
        response = client.get_me()
        assert_status(response,401)









