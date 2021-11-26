import logging
import json
from typing import List

from model.food import Food
from model.order import Order, OrderFood

import lib.errors as errors
import lib.imgur as imgur

import repository.food as foodRepository
import repository.order as orderRepository

logger = logging.getLogger('API Handler')

def AllFoods() -> str:
    try:
        foods = foodRepository.GetAll()

    except Exception as e:
        logger.exception(e)
        raise
    
    jsonList = []

    for food in foods:
        jsonList.append(food.__dict__)

    return json.dumps(jsonList, default=str)

def FoodByID(id: int) -> str:
    try:
        food = foodRepository.GetByID(id)

    except Exception as e:
        logger.exception(e)
        raise

    if food is None:
        raise errors.FoodNotFound('id', id)

    return json.dumps(food.__dict__, default=str)

def FoodByName(name: str) -> str:
    try:
        food = foodRepository.GetByName(name)

    except Exception as e:
        logger.exception(e)
        raise

    if food is None:
        raise errors.FoodNotFound('name', name)

    return json.dumps(food.__dict__, default=str)

def RegisterFood(data: dict) -> str:
    if not ('name' in data and 'price' in data and 'image' in data):
        raise errors.BadRequest('missing or invalid fields')

    try:
        link = imgur.UploadImage(data['image'], data['name'], data['description'])

    except Exception as e:
        logger.exception(e)
        raise
    
    food = Food({
        'name': data['name'],
        'price': data['price'],
        'image_url': link,
    })

    if 'quantity' in data:
        food.quantity = data['quantity']

    if 'description' in data:
        food.description = data['description']

    try:
        foodRepository.Create(food)
    
    except Exception as e:
        logger.exception(e)
        raise

    return json.dumps({'response': 'OK'})

def RegisterOrder(data: dict) -> str:    
    if not ('destiny' in data and 'total_value' in data and 'foods' in data):
        raise errors.BadRequest('missing payload fields')

    if not (isinstance(data['destiny'], str) and isinstance(data['total_value'], float) and isinstance(data['foods'], list)):
        raise errors.BadRequest('invalid payload fields types')

    order = Order({
        'destiny': data['destiny'],
        'total_value': data['total_value'],
    })

    update_foods_payload: List[dict] = []

    for order_food in data['foods']:
        if not (isinstance(order_food, dict)):
            raise errors.BadRequest('invalid order foods payload field type')
        
        if not ('id' in order_food and 'quantity' in order_food):
            raise errors.BadRequest('missing order foods payload fields')
        
        try:
            food = foodRepository.GetByID(order_food['id'])
        
        except Exception as e:
            logger.exception(e)
            raise

        if food is None:
            raise errors.FoodNotFound('id', order_food['id'])

        if food.quantity < order_food['quantity']:
            raise errors.FoodOutOfStock('name', food.name)

        order.foods.append(OrderFood(food, order_food['quantity']))
        update_foods_payload.append({'id': food.id, 'quantity_to_subtract': order_food['quantity']})

    try:
        foodRepository.UpdateFoodsQuantity(update_foods_payload)
    except Exception as e:
        if e != errors.FoodOutOfStock:
            logger.exception(e)
        
        raise

    #Criar order antes ou pensar em uma forma de incluir essa criação na transaction que atualiza a quantidade das comidas
    #Ou então fazer de um outro jeito essas transactions de forma que eu possa controlar o banco pelo handler aqui, como externalizar funcao de commit
    #e de rollback,similar ao que temos no letras
    try:
        orderRepository.Create(order)
    except Exception as e:
        logger.exception(e)
        raise

    return json.dumps({'response': 'OK'})