import requests
from config.settings import BASE_URL

class ApiClient:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.token = None
    
    def set_token(self,token):
        self.token = token
        self.session.headers["Authorization"] = f"Bearer {token}"

    def clear_auth(self):
        self.token = None
        self.session.headers.pop("Authorization",None)
    
    def register(self,payload):
        return self.session.post(f"{self.base_url}/auth/register",json=payload)
    
    def login(self,username,password):
        return self.session.post(
           f"{self.base_url}/auth/login",data={"username":username,"password":password}
        )
    
    def get_me(self):
        return self.session.get(
           f"{self.base_url}/auth/me"
        )
    def list_users(self,skip=0,limit=20):
        return self.session.get(
            f"{self.base_url}/users",params={"skip":skip,"limit":limit}
        )
    def get_user(self,user_id):
        return self.session.get(
            f"{self.base_url}/users/{user_id}"
        )
    def delete_user(self,user_id):
        return self.session.delete(
           f"{self.base_url}/users/{user_id}"
        )
    def update_user(self,user_id,payload):
        return self.session.put(
            f"{self.base_url}/users/{user_id}",json=payload
        )

        
    def create_product(self,payload):
        return self.session.post(
            f"{self.base_url}/products",json=payload
        )
    def list_products(self,skip=0,limit=20):
        return self.session.get(
            f"{self.base_url}/products/",params={"skip":skip,"limit":limit}
        )
    
    def get_product(self,product_id):
        return self.session.get(
            f"{self.base_url}/products/{product_id}"
        )
    def update_product(self,product_id,payload):
        return self.session.put(
            f"{self.base_url}/products/{product_id}",json=payload
        )
    def delete_product(self,product_id):
        return self.session.delete(
            f"{self.base_url}/products/{product_id}"
        )
    def health_check(self):
        return self.session.get(f"{self.base_url}/")




