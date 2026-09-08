def assert_status(response,expected):
    assert response.status_code == expected ,(
        f"expected {expected}  got{response.status_code}." 
        f"Body:{response.text}"

    )
def assert_json_has_keys(response,keys):
    data =response.json()
    for key in keys :
        assert key in data, f"missing key {key} in data {data}"

def assert_error(response,expected_status,detail_contains=None):
    assert_status(response,expected_status)
    if detail_contains:
        detail = response.json().get("detail")
        assert detail_contains.lower() in detail.lower() , f"expected {detail_contains},got {detail}"

