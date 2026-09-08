import pytest
from utils.assertions import assert_status

@pytest.mark.smoke
def test_healthcheck(client):
    response = client.health_check()
    assert_status(response,200)

