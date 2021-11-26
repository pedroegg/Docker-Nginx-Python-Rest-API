import datetime
from typing import List

from model.food import Food

class Order():
    def __init__(self, data: dict):
        self.id = None
        self.destiny: str = str(data['destiny'])
        self.total_value: float = float(data['total_value'])
        self.foods: List[OrderFood] = []
        self.created_at: datetime.datetime = None
        self.updated_at: datetime.datetime = None

        if 'id' in data:
            self.id = int(data['id'])

        if 'created_at' in data:
            self.created_at = datetime.datetime.strptime(str(data['created_at']), '%Y-%m-%d %H:%M:%S')
        
        if 'updated_at' in data:
            self.updated_at = datetime.datetime.strptime(str(data['updated_at']), '%Y-%m-%d %H:%M:%S')


class OrderFood():
    def __init__(self, food: Food, quantity: int):
        self.food: Food = food
        self.quantity: int = quantity
