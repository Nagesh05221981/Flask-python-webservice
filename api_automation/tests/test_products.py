import pytest
import allure
from utils.assertions import assert_status
from utils.test_data import generate_product
from schemas.validators import validate_product, validate_product_list


@allure.feature("Products")
@pytest.mark.products
class TestCreateProduct:

    def test_create_product(self, authenticated_client):
        """Create a new product — expect 201 and valid product object."""
        product = generate_product()
        response = authenticated_client.create_product(product)
        assert_status(response, 201)
        validate_product(response.json())

    def test_create_product_no_auth(self, client):
        """Create product without token — expect 401."""
        product = generate_product()
        response = client.create_product(product)
        assert_status(response, 401)


@allure.feature("Products")
@pytest.mark.products
class TestListProducts:

    def test_list_products(self, authenticated_client):
        """List all products — expect 200 and a list."""
        response = authenticated_client.list_products()
        assert_status(response, 200)
        validate_product_list(response.json())


@allure.feature("Products")
@pytest.mark.products
class TestGetProduct:

    def test_get_product_by_id(self, authenticated_client, created_product):
        """Get a product by ID — expect 200 and valid product object."""
        product_id = created_product["id"]
        response = authenticated_client.get_product(product_id)
        assert_status(response, 200)
        validate_product(response.json())

    def test_get_product_not_found(self, authenticated_client):
        """Get a product that doesn't exist — expect 404."""
        response = authenticated_client.get_product(99999)
        assert_status(response, 404)


@allure.feature("Products")
@pytest.mark.products
class TestUpdateProduct:

    def test_update_own_product(self, authenticated_client, created_product):
        """Update your own product — expect 200 and updated values."""
        product_id = created_product["id"]
        response = authenticated_client.update_product(
            product_id, {"name": "Updated Name", "price": 99.99}
        )
        assert_status(response, 200)
        assert response.json()["name"] == "Updated Name"
        assert response.json()["price"] == 99.99


@allure.feature("Products")
@pytest.mark.products
class TestDeleteProduct:

    def test_delete_own_product(self, authenticated_client, created_product):
        """Delete your own product — expect 204, then verify it's gone."""
        product_id = created_product["id"]
        response = authenticated_client.delete_product(product_id)
        assert_status(response, 204)

        # Confirm it's deleted
        response = authenticated_client.get_product(product_id)
        assert_status(response, 404)
