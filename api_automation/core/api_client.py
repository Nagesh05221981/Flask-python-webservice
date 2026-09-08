import requests
from config.settings import BASE_URL

class ApiClient:
    def __init__(self):
        #override base_url using env configuration BASE_URL
        self.base_url = BASE_URL
        # Session persists cookies and headers across multiple requests
        self.session = requests.Session()
        self.token = None

    def set_token(self,token):
        """Store the JWT token and set it as Authorization header
        for all future requests."""
        self.token = token
        self.session.headers["Authorization"]= f"Bearer {token}"

    def clear_auth(self):
        """Remove the token and Authorization header —
         makes the client unauthenticated again."""
        self.token = None
        self.session.headers.pop("Authorization",None)


    # -------Auth end points

    def register(self,payload):
        """
         send http post request with payload
        POST /auth/register — create a new user account. Payload is JSON
        """
        return self.session.post(f"{self.base_url}/auth/register",json=payload)

    def login(self,username,password):
        """POST /auth/login — authenticate with form data, returns JWT token."""
        return self.session.post(f"{self.base_url}/auth/login",data={"username":username,"password":password})

    def get_me(self):
        """GET /auth/me — get the currently logged-in user's profile.
        Requires Bearer token."""
        return self.session.get(f"{self.base_url}/auth/me")

    # -------User end points (all require Bearer token)

    def list_users(self,skip=0,limit=20):
        """GET /users/ — list all users with pagination."""
        return self.session.get(f"{self.base_url}/users/",params={"skip":skip,"limit":limit})

    def get_user(self,user_id):
        """GET /users/{id} — get a single user by ID."""
        return self.session.get(f"{self.base_url}/users/{user_id}")

    def update_user(self,user_id,payload):
        """PUT /users/{id} — update a user. Users can only update themselves (403 otherwise)."""
        return self.session.put(f"{self.base_url}/users/{user_id}",json=payload)

    def delete_user(self,user_id):
        """DELETE /users/{id} — delete a user. Users can only delete themselves (403 otherwise)."""
        return self.session.delete(f"{self.base_url}/users/{user_id}")

    # ------Products (all require Bearer token) ---------

    def create_product(self,payload):
        """POST /products/ — create a new product owned by the current user."""
        return self.session.post(f"{self.base_url}/products/",json=payload)

    def list_products(self,skip=0,limit=20):
        """GET /products/ — list all products with pagination."""
        return self.session.get(f"{self.base_url}/products/",params={"skip":skip,"limit":limit})

    def get_product(self,product_id):
        """GET /products/{id} — get a single product by ID."""
        return self.session.get(f"{self.base_url}/products/{product_id}")

    def update_product(self,product_id,payload):
        """PUT /products/{id} — update a product. Only the owner can update (403 otherwise)."""
        return self.session.put(f"{self.base_url}/products/{product_id}",json=payload)

    def delete_product(self,product_id):
        """DELETE /products/{id} — delete a product. Only the owner can delete (403 otherwise)."""
        return self.session.delete(f"{self.base_url}/products/{product_id}")

    # --- API Key auth ---

    def set_api_key(self,api_key):
        """Set X-API-Key header for API key authentication."""
        self.session.headers["X-API-Key"] = api_key

    # --- OAuth ---

    def oauth_login(self):
        """GET /auth/oauth/login — get the dummy OAuth authorization URL."""
        return self.session.get(f"{self.base_url}/auth/oauth/login")

    def oauth_callback(self,code):
        """POST /auth/oauth/callback — exchange OAuth code for a JWT token."""
        return self.session.post(f"{self.base_url}/auth/oauth/callback",json={"code":code})

    # --- Health ---

    def health_check(self):
        """GET / — simple health check, no auth required."""
        return self.session.get(f"{self.base_url}/")
