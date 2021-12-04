from enum import auto
from typing import List, Optional

from lib.mysql import MySQL
from model.food import Food
from model.order import Order, OrderFood

import lib.errors as errors

def GetAll() -> List[Order]:
    query = "SELECT * FROM sushi2go.order"

    try:
        result, _ = MySQL().execute(query)
    except:
        raise

    orders: List[Order] = []

    for row in result:
        orders.append(Order(row))

    return orders

def GetByID(id: int) -> Optional[Order]:
    query = "SELECT * FROM sushi2go.order WHERE id = ?"

    try:
        result, _ = MySQL().execute(query, params=(id,), usePrepared=True)
    except:
        raise

    if len(result) == 0:
        return None

    return Order(result[0])

def GetAllWithFoods() -> List[Order]:
    query = "SELECT * FROM sushi2go.order"

    try:
        result, _ = MySQL().execute(query)
    except:
        raise

    orders: List[Order] = []

    for row in result:
        order = Order(row)

        query = """
            SELECT
                of.food_quantity,
                f.*
            FROM sushi2go.order AS o
            INNER JOIN sushi2go.order_food AS of ON(o.id = of.order_id)
            INNER JOIN sushi2go.food AS f ON(f.id = of.food_id)
            WHERE o.id = ?
        """

        try:
            resultFoods, _ = MySQL().execute(query, params=(order.id,), usePrepared=True)
        except:
            raise

        for foodRow in resultFoods:
            order.foods.append(OrderFood(Food(foodRow), foodRow['food_quantity']))

        orders.append(order)

    return orders

def GetByIDWithFoods(id: int) -> Optional[Order]:
    query = "SELECT * FROM sushi2go.order WHERE id = ?"

    try:
        result, _ = MySQL().execute(query, params=(id,), usePrepared=True)
    except:
        raise

    if len(result) == 0:
        return None

    order = Order(result[0])

    query = """
        SELECT
            of.food_quantity,
            f.*
        FROM sushi2go.order AS o
        INNER JOIN sushi2go.order_food AS of ON(o.id = of.order_id)
        INNER JOIN sushi2go.food AS f ON(f.id = of.food_id)
        WHERE o.id = ?
    """

    try:
        result, _ = MySQL().execute(query, params=(id,), usePrepared=True)
    except:
        raise

    for row in result:
        order.foods.append(OrderFood(Food(row), row['food_quantity']))

    return order

def Create(order: Order) -> None:
    query = "INSERT INTO sushi2go.order (`destiny`, `total_value`, `phone_number`) VALUES (?, ?, ?)"

    try:
        _, last_inserted_id = MySQL().execute(query, params=(order.destiny, order.total_value, order.phone_number,), usePrepared=True, autoCommit=False)
    except:
        raise
    
    if last_inserted_id is None:
        try:
            MySQL().rollback()
        except:
            raise errors.InternalError('failed to create order')

        raise errors.InternalError('failed to create order')
    
    order.id = last_inserted_id

    for orderFood in order.foods:
        query = "INSERT INTO sushi2go.order_food (`order_id`, `food_id`, `food_quantity`) VALUES (?, ?, ?)"

        try:
            MySQL().execute(query, params=(order.id, orderFood.food.id, orderFood.quantity,), usePrepared=True, autoCommit=False)
        except:
            raise

    try:
        MySQL().commit()
    except:
        raise errors.InternalError('failed to create order')

    return 
