import datetime

class User():
    def __init__(self, data: dict):
        self.id = None
        self.username: str = str(data['username'])
        self.password: str = str(data['password'])
        self.created_at: datetime.datetime = None
        self.updated_at: datetime.datetime = None

        if 'id' in data:
            self.id = int(data['id'])
