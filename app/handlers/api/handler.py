import logging
import json
from typing import List, Optional, Tuple
from passlib.hash import bcrypt

from model.food import Food
from model.order import Order, OrderFood
from model.user import User

import lib.errors as errors
import lib.imgur as imgur
import lib.jwt as jwt
import lib.admin as admin

import repository.food as foodRepository
import repository.order as orderRepository
import repository.user as userRepository

logger = logging.getLogger('API Handler')

def Login(data: dict) -> Tuple[str, str]:
    if not ('username' in data and 'password' in data):
        raise errors.BadRequest('missing username or password fields')

    if not (isinstance(data['username'], str) and isinstance(data['password'], str)):
        raise errors.BadRequest('invalid payload fields types')

    try:
        user = userRepository.GetByUsername(data['username'])
    
    except Exception as e:
        logger.exception(e)
        raise

    if user is None:
        raise errors.UserNotFound()

    try:
        hasher = bcrypt.using(rounds=13)
        if not hasher.verify(data['password'], user.password):
            raise errors.IncorrectPassword()

    except Exception as e:
        if e is not errors.IncorrectPassword:
            logger.exception(e)
        
        raise
    
    try:
        jwt_data = jwt.Encode(user.id, user.username, admin.IsAdminByUserID(user.id))
    
    except Exception as e:
        logger.exception(e)
        raise

    return json.dumps({'response': 'OK'}), jwt_data

def Register(data: dict) -> str:
    if not ('username' in data and 'password' in data):
        raise errors.BadRequest('missing username or password fields')

    if not (isinstance(data['username'], str) and isinstance(data['password'], str)):
        raise errors.BadRequest('invalid payload fields types')

    try:
        user = userRepository.GetByUsername(data['username'])
    
    except Exception as e:
        logger.exception(e)
        raise

    if user is not None:
        raise errors.UserAlreadyExists()

    try:
        hasher = bcrypt.using(rounds=13)
        hashed_password = hasher.hash(data['password'])

    except Exception as e:
        logger.exception(e)
        raise

    try:
        userRepository.Create(User({'username': data['username'], 'password': hashed_password}))
    
    except Exception as e:
        logger.exception(e)
        raise
    
    return json.dumps({'response': 'OK'})

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

def FilterFoods(query: Optional[str]) -> str:
    if query is None or query == '':
        return AllFoods()
    
    try:
        foods = foodRepository.Filter(query)

    except Exception as e:
        logger.exception(e)
        raise
    
    jsonList = []

    for food in foods:
        jsonList.append(food.__dict__)

    return json.dumps(jsonList, default=str)

def RegisterFood(data: dict) -> str:
    if not ('name' in data and 'price' in data and 'image' in data):
        raise errors.BadRequest('missing or invalid fields')

    if not (isinstance(data['name'], str) and isinstance(data['price'], float) and isinstance(data['image'], str)):
        raise errors.BadRequest('invalid payload fields types')

    if 'quantity' in data and not isinstance(data['quantity'], int):
        raise errors.BadRequest('invalid quantity payload field type')

    if 'description' in data and not isinstance(data['description'], str):
        raise errors.BadRequest('invalid description payload field type')

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

def EditFood(id: int, data: dict) -> str:
    if not ('name' in data and 'price' in data):
        raise errors.BadRequest('missing or invalid fields')

    if not (isinstance(data['name'], str) and isinstance(data['price'], float)):
        raise errors.BadRequest('invalid payload fields types')

    if 'quantity' in data and not isinstance(data['quantity'], int):
        raise errors.BadRequest('invalid quantity payload field type')

    if 'description' in data and not isinstance(data['description'], str):
        raise errors.BadRequest('invalid description payload field type')

    try:
        food = foodRepository.GetByID(id)
    
    except Exception as e:
        logger.exception(e)
        raise

    if food is None:
        raise errors.FoodNotFound('id', id)

    food.name = data['name']
    food.price = data['price']

    if 'quantity' in data:
        food.quantity = data['quantity']

    if 'description' in data:
        food.description = data['description']

    try:
        foodRepository.Update(food)
    
    except Exception as e:
        logger.exception(e)
        raise

    return json.dumps({'response': 'OK'})

def DeleteFood(id: int) -> str:
    try:
        food = foodRepository.GetByID(id)
    
    except Exception as e:
        logger.exception(e)
        raise

    if food is None:
        raise errors.FoodNotFound('id', id)

    try:
        foodRepository.Delete(id)
    
    except Exception as e:
        logger.exception(e)
        raise

    return json.dumps({'response': 'OK'})

def AllOrders() -> str:
    try:
        orders = orderRepository.GetAllWithFoods()

    except Exception as e:
        logger.exception(e)
        raise
    
    jsonList = []

    for order in orders:
        d = order.__dict__
        d['foods'] = [{'food': orderFood.food.__dict__, 'quantity': orderFood.quantity} for orderFood in order.foods]

        jsonList.append(d)

    return json.dumps(jsonList, default=str)

def OrderByID(id: int) -> str:
    try:
        order = orderRepository.GetByIDWithFoods(id)

    except Exception as e:
        logger.exception(e)
        raise

    if order is None:
        raise errors.OrderNotFound('id', id)

    d = order.__dict__
    d['foods'] = [{'food': orderFood.food.__dict__, 'quantity': orderFood.quantity} for orderFood in order.foods]

    return json.dumps(d, default=str)

def RegisterOrder(data: dict) -> str:    
    if not ('destiny' in data and 'total_value' in data and 'phone_number' in data and 'foods' in data):
        raise errors.BadRequest('missing payload fields')

    if not (isinstance(data['destiny'], str) and 
        isinstance(data['total_value'], float) and 
        isinstance(data['phone_number'], str) and 
        isinstance(data['foods'], list)
    ):
        raise errors.BadRequest('invalid payload fields types')

    order = Order({
        'destiny': data['destiny'],
        'total_value': data['total_value'],
        'phone_number': data['phone_number'],
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

    try:
        orderRepository.Create(order)
    except Exception as e:
        logger.exception(e)
        raise

    return json.dumps({'response': 'OK'})
