"""
These functions check that
API responses contain the expected fields.

Simple validators (is_valid_*) just check key presence.
Schema validators (validate_*) check types, required fields, and value constraints.
"""

from jsonschema import validate, ValidationError


# --- Simple key-presence validators ---

USER_KEYS = ["id","username","email","is_active","api_key"]
PRODUCT_KEYS = ["id","name","description","price","in_stock","owner_id"]
TOKEN_KEYS = ["access_token","token_type"]

def is_valid_user(data):
    """Check if data contains all expected user fields. Returns True or False."""
    return all(key in data for key in USER_KEYS)

def is_valid_product(data):
    return all(key in data for key in PRODUCT_KEYS)

def is_valid_token(data):
    return all(key in data for key in TOKEN_KEYS)


# --- JSON Schema definitions ---

USER_SCHEMA = {
    "type": "object",
    "required": ["id", "username", "email", "is_active", "api_key"],
    "properties": {
        "id": {"type": "integer"},
        "username": {"type": "string", "minLength": 1},
        "email": {"type": "string", "format": "email"},
        "is_active": {"type": "boolean"},
        "api_key": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}

PRODUCT_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "description", "price", "in_stock", "owner_id"],
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string", "minLength": 1},
        "description": {"type": "string"},
        "price": {"type": "number", "minimum": 0},
        "in_stock": {"type": "boolean"},
        "owner_id": {"type": "integer"},
    },
    "additionalProperties": False,
}

TOKEN_SCHEMA = {
    "type": "object",
    "required": ["access_token", "token_type"],
    "properties": {
        "access_token": {"type": "string", "minLength": 1},
        "token_type": {"type": "string", "enum": ["bearer"]},
    },
    "additionalProperties": False,
}

USER_LIST_SCHEMA = {
    "type": "array",
    "items": USER_SCHEMA,
}

PRODUCT_LIST_SCHEMA = {
    "type": "array",
    "items": PRODUCT_SCHEMA,
}


# --- Schema validation functions ---

def validate_user(data):
    """Validate data matches the full user schema (types + required fields)."""
    validate(instance=data, schema=USER_SCHEMA)

def validate_product(data):
    """Validate data matches the full product schema."""
    validate(instance=data, schema=PRODUCT_SCHEMA)

def validate_token(data):
    """Validate data matches the token schema."""
    validate(instance=data, schema=TOKEN_SCHEMA)

def validate_user_list(data):
    """Validate data is a list of valid user objects."""
    validate(instance=data, schema=USER_LIST_SCHEMA)

def validate_product_list(data):
    """Validate data is a list of valid product objects."""
    validate(instance=data, schema=PRODUCT_LIST_SCHEMA)
