import pytest
from utils.test_data import generate_product

@pytest.fixture
def created_product(authenticated_client):
    """
    create a product using a authenticated user
    returns product data
    """ 
    product_data = generate_product()
    response = authenticated_client.create_product(product_data)
    assert response.status_code == 201
    return response.json()

