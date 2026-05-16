from core.swagger_loader import SwaggerLoader
from core.api_client import ApiClient


class TestBuilder:
    def __init__(self, spec_path, base_url):
        self.loader = SwaggerLoader(spec_path)
        self.client = ApiClient(base_url)

    def generate_tests(self):
        """Parse the spec and return (method, path, body, expected_status) tuples."""
        spec = self.loader.load()
        tests = []

        for path, methods in spec.get("paths", {}).items():
            for method, details in methods.items():
                # Extract request body example and content type
                body = None
                content_type = "application/json"
                request_body = details.get("requestBody", {})
                content = request_body.get("content", {})
                if "application/json" in content:
                    body = content["application/json"].get("example")
                elif "application/x-www-form-urlencoded" in content:
                    body = content["application/x-www-form-urlencoded"].get("example")
                    content_type = "application/x-www-form-urlencoded"

                # Extract the first (primary) expected status code
                responses = details.get("responses", {})
                expected_status = 200
                if responses:
                    first_code = list(responses.keys())[0]
                    expected_status = int(first_code)

                # Resolve path parameters from examples
                resolved_path = path
                for param in details.get("parameters", []):
                    if param.get("in") == "path" and "example" in param:
                        placeholder = "{" + param["name"] + "}"
                        resolved_path = resolved_path.replace(
                            placeholder, str(param["example"])
                        )

                tests.append((method.upper(), resolved_path, body, expected_status, content_type))

        return tests
