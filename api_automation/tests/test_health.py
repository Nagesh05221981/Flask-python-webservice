import pytest
import allure
from utils.assertions import assert_status


@allure.feature("Health")
@pytest.mark.smoke
def test_healthcheck(client):
    with allure.step("Call health check endpoint"):
        response = client.health_check()
    with allure.step("Verify status 200"):
        assert_status(response, 200)
