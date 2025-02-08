from sql.model import Model

class Post(Model):
    def __init__(self):
        super().__init__()
    def insert_post(self, data):
        return self.post("post-web/store", data=data)
    
    def find_post(self,id):
        return self.get(f"post-web/{id}")

    def get_none_post_ids(self, data):
        return self.post("post-web/none", data=data)