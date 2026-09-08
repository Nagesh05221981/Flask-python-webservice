
def assert_status(response,expected):
    assert response.status_code == expected , (
        f"Expected {expected},got {response.status_code}. "
        f"Body: {response.text}"
    )

def assert_json_has_keys(response,keys):
    data = response.json()
    for key in keys:
        assert key in data , f"missing key  {key} in response data:{data}"
def assert_error(response,expected_status,detail_contains=None):
    """                                                                                                                                                                                                                                                                                                                                                                 
      This function checks the error status code
      and optionally checks the error message                                                                                                                                                                                                                                                                                                                             
      in the response body.
      validates that an API error response is correct — 
      both the status code and the error message                                                                                                                                                                                                                                                                                                                                             
      """

    assert_status(response,expected_status)
    if detail_contains:
        detail = response.json().get("detail","")
        assert detail_contains.lower() in detail.lower(),(
            f"Expected {detail_contains} got {detail}"
        )


