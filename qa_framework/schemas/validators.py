USER_KEYS = ["id","username","email","is_active","api_key"]
PRODUCT_KEYS = ["id","name","description","price","in_stock","owner_id"]
TOKEN_KEYS = ["access_token","token_type"]

def is_valid_user(data):
    return all( key in data for key in USER_KEYS )

def is_valid_product(data):
    return all (key in data for key in PRODUCT_KEYS )

def is_valid_token(data):
    return all(key in data for key in TOKEN_KEYS)
