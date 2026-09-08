import uuid
def generate_user():
    unique = uuid.uuid4().hex[:8]
    return {
        "username" : f"user_{unique}",
        "password" : "Testpass1234",
        "email" : f"user_{unique}@test.com"
    }

def generate_product():
    unique = uuid.uuid4().hex[:8]
    return {
        "name": f"Product_{unique}",
        "description": f"test product {unique}",
        "price": 20.0,
        "in_stock": True
    }