import requests


class ApiClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None
        self.api_key = None

    def authenticate(self, username, password):
        """Login and store the JWT token for subsequent requests."""
        response = requests.post(
            self.base_url + "/auth/login",
            data={"username": username, "password": password},
        )
        response.raise_for_status()
        self.token = response.json()["access_token"]

    def set_api_key(self, api_key):
        """Set an API key for subsequent requests."""
        self.api_key = api_key

    def _build_headers(self):
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    def request(self, method, path, json=None, content_type="application/json"):
        url = self.base_url + path
        if content_type == "application/x-www-form-urlencoded" and json is not None:
            response = requests.request(method, url, headers=self._build_headers(), data=json)
        else:
            response = requests.request(method, url, headers=self._build_headers(), json=json)
        return response