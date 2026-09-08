import uuid
def generate_user():
    unique = uuid.uuid4().hex[:8]
    return {
        "username": f"user_{unique}",
        "password": "TestPass1234",
        "email": f"user_{unique}@test.com",
    }

def generate_product():
    unique = uuid.uuid4().hex[:8]
    return {
        "name" : f"Product_{unique}",
        "description": f"Test Product {unique}",
        "price": 19.99,
        "in_stock": True
    }