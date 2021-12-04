from typing import List, Optional

from lib.mysql import MySQL
from model.food import Food

import lib.errors as errors

def GetAll() -> List[Food]:
    query = "SELECT * FROM sushi2go.food"

    try:
        result, _ = MySQL().execute(query)
    except:
        raise

    foods: List[Food] = []

    for row in result:
        foods.append(Food(row))

    return foods

def Filter(q: str) -> List[Food]:
    query = "SELECT * FROM sushi2go.food WHERE name LIKE CONCAT('%', ?, '%')"

    try:
        result, _ = MySQL().execute(query, (q,), usePrepared=True)
    except:
        raise

    foods: List[Food] = []

    for row in result:
        foods.append(Food(row))

    return foods

def GetByID(id: int) -> Optional[Food]:
    query = "SELECT * FROM sushi2go.food WHERE id = ?"

    try:
        result, _ = MySQL().execute(query, (id,), usePrepared=True)
    except:
        raise

    if len(result) == 0:
        return None

    return Food(result[0])

def GetByName(slug: str) -> Optional[Food]:
    query = "SELECT * FROM sushi2go.food WHERE name = ?"

    try:
        result, _ = MySQL().execute(query, (slug,), usePrepared=True)
    except:
        raise

    if len(result) == 0:
        return None

    return Food(result[0])

def Create(food: Food) -> None:
    query = "INSERT INTO sushi2go.food (`name`, `description`, `quantity`, `price`, `image_url`) VALUES (?, ?, ?, ?, ?)"

    try:
        MySQL().execute(query, (food.name, food.description, food.quantity, food.price, food.imageURL,), usePrepared=True)
    except:
        raise

    return

def Update(food: Food) -> None:
    query = "UPDATE sushi2go.food SET name = ?, description = ?, quantity = ?, price = ? WHERE id = ?"

    try:
        MySQL().execute(query, (food.name, food.description, food.quantity, food.price, food.id,), usePrepared=True)
    except:
        raise

    return

def Delete(id: int) -> None:
    query = "DELETE FROM sushi2go.food WHERE id = ?"

    try:
        MySQL().execute(query, (id,), usePrepared=True)
    except:
        raise

    return

def UpdateFoodsQuantity(foods_payload: List[dict]) -> None:
    queries = []

    for food_p in foods_payload:
        query = "UPDATE sushi2go.food SET quantity = quantity - ? WHERE id = ?"

        try:
            queries.append(MySQL().query(query, (food_p['quantity_to_subtract'], food_p['id'],), usePrepared=True))
        except:
            raise

    def do_after(current_query):
        food = GetByID(current_query.params[1])
        if food is not None and food.quantity < 0:
            raise errors.FoodOutOfStock('name', food.name)

    try:
        MySQL().executeTransactionQueries(queries, do_after_each=do_after)
    except:
        raise

    return 
