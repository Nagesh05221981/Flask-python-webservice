import yaml


class SwaggerLoader:
    def __init__(self, spec_path):
        self.spec_path = spec_path

    def load(self):
        with open(self.spec_path, "r") as f:
            return yaml.safe_load(f)



