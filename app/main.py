import eventlet
eventlet.monkey_patch()

from typing import Tuple
import datetime

import flask
from flask import Flask, request
from flask_socketio import SocketIO
from werkzeug.exceptions import HTTPException

import json
import logging

import handlers.api.handler as APIHandler
import lib.errors as errors
import lib.admin as admin
import lib.jwt as jwt

app = Flask(__name__)
socketio = SocketIO(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("APP")

def answer(res) -> Tuple[str, int, dict]:
    return res, 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/food/<int:id>', methods=['GET'])
def GetFoodByID(id: int):
    return answer(APIHandler.FoodByID(id))

@app.route('/foods', methods=['GET'])
def GetFoods():
    return answer(APIHandler.AllFoods())

@app.route('/foods/filter')
def FilterFoods():
    query = request.args.get('q')
    return answer(APIHandler.FilterFoods(query))

@app.route('/food/create', methods=['POST'])
def CreateFood():
    if not request.is_json:
        raise errors.BadRequest('invalid json body')

    active_jwt = request.cookies.get('jwt')
    if not jwt.IsValid(active_jwt):
        raise errors.NotLoggedIn()

    if not admin.IsAdminByCookie(active_jwt):
        raise errors.NotAdmin()

    return answer(APIHandler.RegisterFood(request.get_json()))

@app.route('/food/<int:id>/edit', methods=['POST'])
def EditFood(id: int):
    if not request.is_json:
        raise errors.BadRequest('invalid json body')

    active_jwt = request.cookies.get('jwt')
    if not jwt.IsValid(active_jwt):
        raise errors.NotLoggedIn()

    if not admin.IsAdminByCookie(active_jwt):
        raise errors.NotAdmin()

    return answer(APIHandler.EditFood(id, request.get_json()))

@app.route('/food/<int:id>/delete', methods=['DELETE'])
def DeleteFood(id: int):
    active_jwt = request.cookies.get('jwt')
    if not jwt.IsValid(active_jwt):
        raise errors.NotLoggedIn()

    if not admin.IsAdminByCookie(active_jwt):
        raise errors.NotAdmin()

    return answer(APIHandler.DeleteFood(id))

@app.route('/order/<int:id>', methods=['GET'])
def GetOrderByID(id: int):
    return answer(APIHandler.OrderByID(id))

@app.route('/orders', methods=['GET'])
def GetOrders():
    return answer(APIHandler.AllOrders())

@app.route('/order/create', methods=['POST'])
def CreateOrder():
    if not request.is_json:
        raise errors.BadRequest('invalid json body')

    active_jwt = request.cookies.get('jwt')
    if not jwt.IsValid(active_jwt):
        raise errors.NotLoggedIn()

    return answer(APIHandler.RegisterOrder(request.get_json()))

@app.route('/login', methods=['POST'])
def Login():
    if not request.is_json:
        raise errors.BadRequest('invalid json body')

    active_jwt = request.cookies.get('jwt')
    if jwt.IsValid(active_jwt):
        raise errors.AlreadyLoggedIn()

    r, new_jwt = APIHandler.Login(request.get_json())

    res = flask.make_response()
    res.set_cookie('jwt', value=new_jwt, expires=datetime.datetime.today() + datetime.timedelta(days=1), secure=False)
    res.set_data(r)

    return answer(res)

@app.route('/logout', methods=['POST'])
def Logout():
    active_jwt = request.cookies.get('jwt')
    if not jwt.IsValid(active_jwt):
        raise errors.NotLoggedIn()
    
    res = flask.make_response()
    res.set_cookie('jwt', '', expires=datetime.datetime.now(), secure=False)
    res.set_data(json.dumps({'response': 'OK'}))

    return answer(res)

@app.route('/register', methods=['POST'])
def Register():
    if not request.is_json:
        raise errors.BadRequest('invalid json body')

    active_jwt = request.cookies.get('jwt')
    if jwt.IsValid(active_jwt):
        raise errors.AlreadyLoggedIn()

    return answer(APIHandler.Register(request.get_json()))

@app.route('/isAdmin', methods=['GET'])
def IsAdmin():
    active_jwt = request.cookies.get('jwt')
    
    return answer(json.dumps({'response': admin.IsAdminByCookie(active_jwt)}))

@app.errorhandler(HTTPException)
def handle_exception(e: HTTPException):
    response = e.get_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"

    return response

@app.errorhandler(Exception)
def handle_exception(e: Exception):
    if isinstance(e, HTTPException):
        return e

    logger.error(e, exc_info=1)
    return json.dumps({"error": 'something wrong occurred'}), 500, {'Content-Type': 'application/json; charset=utf-8'}

#if __name__ == '__main__':
    #socketio.run(app, "0.0.0.0", "5000")
    #app.run("0.0.0.1", "5000")
    #logging.basicConfig(filename='myapp.log', level=logging.INFO)
