from sql.model import Model

class Domain(Model):
    def __init__(self):
        super().__init__()
    def get_link_by_domain(self,id):
        return self.get(f"domain/get-link/{id}")
