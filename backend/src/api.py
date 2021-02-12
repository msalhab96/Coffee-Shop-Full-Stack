import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


db_drop_and_create_all()


@app.route('/drinks')
def get_drinks():
    """
    this endpoint returns all available drinks from the database
    permission needed: for public
    """
    drinks = [drink.short() for drink in Drink.query.all()]
    return jsonify({
                    "success": True,
                    "drinks": drinks
                    }), 200

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    """
    this endpoint return the detailed description 
    of all drinks, by retreving them from the database 
    ** permission needed: get:drinks-detail
    """
    drinks = [drink.long() for drink in Drink.query.all()]
    return jsonify({
                    "success": True,
                    "drinks": drinks
                    }), 200


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
    """
    this endpoint is used to add a new drink,
    title and recipe should be sent by the user by json header
    ** permission needed: post:drinks
    """
    data = request.get_json()
    if ("title" in data) and ("recipe" in data):
        drink = Drink(
                      title= data["title"], 
                      recipe= json.dumps(data["recipe"])
                      )
        drink.insert()
        return jsonify({
                        "success": True,
                        "drinks": [drink.long()]
                        }), 200
    else:
        return jsonify({
                        "success": False,
                        "drinks": drink
                        }), 401


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth("patch:drinks")
def change_drink(payload, id):
    """
    this endpoint is used to change a certain drink
    for the given drink's id 
    permission needed: patch:drinks
    """
    drink = Drink.query.filter_by(id=id).one_or_none()
    if drink:
        data = request.get_json()
        drink.title = data.get('title')
        drink.recipe = json.dumps(data.get('recipe'))
        drink.update()
        return jsonify({
                        "success": True,
                        "drinks": [drink.long()]
                        }), 200
    else:
        return jsonify({
                        "success": False, 
                        "drinks":[]
                        }), 404

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    """
    this endpoint is used to delete a certain drink
    for the given drink's id 
    permission needed: delete:drinks
    """
    drink = Drink.query.filter_by(id=id).one_or_none()
    if drink:
        drink.delete()
        return jsonify({
                        "success": True, 
                        "delete": id
                        }), 200
    else:
        return jsonify({
                        "success": False, 
                        "delete": id
                        }), 404

@app.errorhandler(422)
def unprocessable(error):
    """
    error to handle 422 errors
    """
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

@app.errorhandler(404)
def badrequest(error):
    """
    error to handle 404 errors
    """
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Bad request!"
    }), 404

@app.errorhandler(AuthError)
def handle_auth_error(error):
    """
    error to handle Auth errors
    """
    response = jsonify(error.error)
    response.status_code = error.status_code
    return response

