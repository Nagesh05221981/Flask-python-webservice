"""Response schema validators for each resource type."""

# Maps field name -> expected type(s) for each resource
USER_SCHEMA = {
    "id": (int,),
    "username": (str,),
    "email": (str,),
    "is_active": (bool,),
    "api_key": (str,),
}

PRODUCT_SCHEMA = {
    "id": (int,),
    "name": (str,),
    "description": (str,),
    "price": (int, float),
    "in_stock": (bool,),
    "owner_id": (int,),
}

TOKEN_SCHEMA = {
    "access_token": (str,),
    "token_type": (str,),
}


def _validate(data, schema):
    """Check that all fields exist and have the correct type.
    Returns (True, "") on success or (False, reason) on failure."""
    for field, expected_types in schema.items():
        if field not in data:
            return False, f"missing field '{field}'"
        if not isinstance(data[field], expected_types):
            actual = type(data[field]).__name__
            expected = "/".join(t.__name__ for t in expected_types)
            return False, f"field '{field}' expected {expected}, got {actual}: {data[field]!r}"
    return True, ""


def is_valid_user(data):
    """Check that a user response has the required fields with correct types."""
    ok, reason = _validate(data, USER_SCHEMA)
    if not ok:
        return False, f"Invalid user: {reason}"
    if "@" not in data["email"]:
        return False, f"Invalid user: email missing '@': {data['email']!r}"
    if len(data["api_key"]) == 0:
        return False, f"Invalid user: api_key is empty"
    return True, ""


def is_valid_product(data):
    """Check that a product response has the required fields with correct types."""
    ok, reason = _validate(data, PRODUCT_SCHEMA)
    if not ok:
        return False, f"Invalid product: {reason}"
    if data["price"] < 0:
        return False, f"Invalid product: negative price {data['price']}"
    return True, ""


def is_valid_token(data):
    """Check that a token response has the required fields with correct types."""
    ok, reason = _validate(data, TOKEN_SCHEMA)
    if not ok:
        return False, f"Invalid token: {reason}"
    if len(data["access_token"]) == 0:
        return False, f"Invalid token: access_token is empty"
    return True, ""
