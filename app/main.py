import eventlet
eventlet.monkey_patch()

from flask import Flask, request
from flask_socketio import SocketIO
from werkzeug.exceptions import HTTPException

import json
import logging

import handlers.api.handler as APIHandler
import lib.errors as errors

app = Flask(__name__)
socketio = SocketIO(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("APP")

@app.route('/food/<int:id>', methods=['GET'])
def GetFoodByID(id: int):
    return APIHandler.FoodByID(id), 200

@app.route('/foods', methods=['GET'])
def GetFoods():
    return APIHandler.AllFoods(), 200

@app.route('/food/create', methods=['POST'])
def CreateFood():
    if not request.is_json:
        raise errors.BadRequest('invalid json body')

    return APIHandler.RegisterFood(request.get_json()), 200

@app.route('/order/<int:id>', methods=['GET'])
def GetOrderByID(id: int):
    return APIHandler.OrderByID(id), 200

@app.route('/orders', methods=['GET'])
def GetOrders():
    return APIHandler.AllOrders(), 200

@app.route('/order/create', methods=['POST'])
def CreateOrder():
    if not request.is_json:
        raise errors.BadRequest('invalid json body')

    return APIHandler.RegisterOrder(request.get_json()), 200

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
    return json.dumps({"error": 'something wrong occurred'}), 500

#if __name__ == '__main__':
    #socketio.run(app, "0.0.0.0", "5000")
    #app.run("0.0.0.1", "5000")
    #logging.basicConfig(filename='myapp.log', level=logging.INFO)
