import pytest
from utils.assertions import assert_status
from utils.test_data import generate_product
from schemas.validators import is_valid_product

@pytest.mark.products
class TestCreateProduct:
    def test_create_product(self,authenticated_client):
        product = generate_product()
        response = authenticated_client.create_product(product)
        assert_status(response,201)
        assert is_valid_product(response.json())

    def test_create_product_no_auth(self,client):
        product = generate_product()
        response = client.create_product(product)
        assert_status(response,401)

@pytest.mark.products
class TestListProducts:
    def test_list_products(self,authenticated_client):
        response = authenticated_client.list_products()
        assert_status(response,200)
        assert isinstance(response.json(),list)

@pytest.mark.products
class TestGetProduct:
    def test_get_product_by_id(self,authenticated_client,created_product):
        product_id = created_product["id"]
        response = authenticated_client.get_product(product_id)
        assert_status(response,200)
        assert is_valid_product(response.json())

    def test_get_product_not_found(self,authenticated_client):
        response = authenticated_client.get_product(123456)
        assert_status(response,404)

@pytest.mark.products
class TestUpdateProduct:
    def test_update_my_product(self,authenticated_client,created_product):
        product_id = created_product["id"]
        response = authenticated_client.update_product(product_id,{"name":"updatedname","price":99})
        assert_status(response,200)
        assert response.json()["name"]== "updatedname"





        