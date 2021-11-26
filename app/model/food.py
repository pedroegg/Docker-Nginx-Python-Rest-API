import datetime

class Food():
    def __init__(self, data: dict):
        self.id = None
        self.name: str = str(data['name'])
        self.price: float = float(data['price'])
        self.imageURL: str = str(data['image_url'])
        self.quantity: int = None
        self.description: str = None
        self.created_at: datetime.datetime = None
        self.updated_at: datetime.datetime = None

        if 'id' in data:
            self.id = int(data['id'])
        
        if 'quantity' in data:
            self.quantity = int(data['quantity'])
        
        if 'description' in data:
            self.description = str(data['description'])

        if 'created_at' in data:
            self.created_at = datetime.datetime.strptime(str(data['created_at']), '%Y-%m-%d %H:%M:%S')
        
        if 'updated_at' in data:
            self.updated_at = datetime.datetime.strptime(str(data['updated_at']), '%Y-%m-%d %H:%M:%S')
