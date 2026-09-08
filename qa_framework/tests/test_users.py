import pytest
from utils.assertions import assert_status,assert_error,assert_json_has_keys
from utils.test_data import generate_user
from schemas.validators import is_valid_user

@pytest.mark.users
class TestListUsers:
    def test_list_users(self,authenticated_client):
        response = authenticated_client.list_users()
        assert_status(response,200)
        assert isinstance(response.json(),list)
    
    def test_list_users_no_auth(self,client):
        response = client.list_users()
        assert_status(response,401)

@pytest.mark.users
class TestGetUser:
    def test_get_user_by_id(self,authenticated_client,registered_user):
        user_id = registered_user["id"]
        response = authenticated_client.get_user(user_id)
        assert_status(response,200)
        assert is_valid_user(response.json())
    def test_get_user_not_found(self,authenticated_client):
        response = authenticated_client.get_user("1234")
        assert_status(response,404)
    
@pytest.mark.users 
class TestUpdateUser:
    def test_update_own_email(self,authenticated_client,registered_user):
        user_id = registered_user["id"]
        response = authenticated_client.update_user(user_id,{"email":"new2@test.com"})
        assert_status(response,200)
        assert response.json()["email"] == "new2@test.com"

    def test_update_other_user_forbidden(self,authenticated_client):
        """ update some other user """
        response = authenticated_client.update_user(1,{"email":"hack@test.com"})
        assert response.status_code in [403,404]

@pytest.mark.users
class TestDeleteUser:
    def test_delete_user_by_id(self,client):
        user_data =generate_user()
        reg = client.register(user_data)
        assert_status(reg,201)
        user_id = reg.json()["id"]
        login = client.login(user_data["username"],user_data["password"])
        client.set_token(login.json()["access_token"])
        response = client.delete_user(user_id)
        assert_status(response,204)
    def test_delete_other_user_forbidden(self,authenticated_client):
        response = authenticated_client.delete_user(1)
        assert response.status_code in [404,403]



        


