from sql.model import Model

class UpdateVersion(Model):
    def __init__(self):
        super().__init__()

    def get_version(self):
        return self.get(f"update-version")
