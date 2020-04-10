import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth
from .utils.formatter import format_drinks_short, format_drinks_long

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''


# db_drop_and_create_all()

## ROUTES


@app.route('/drinks')
def get_drinks():
    """
    @COMPLETED:
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
    """
    drinks = Drink.query.all()
    return jsonify({
        "success": True,
        "error": None,
        "message": "Get drinks successfully.",
        "drinks": format_drinks_short(drinks)
    })


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    """
    @TODO implement endpoint
        GET /drinks-detail
            it should require the 'get:drinks-detail' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    """
    drinks = Drink.query.all()
    return jsonify({
        "success": True,
        "error": None,
        "message": "Get drinks details successfully.",
        "drinks": format_drinks_long(drinks)
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    """
    @TODO implement endpoint
        POST /drinks
            it should create a new row in the drinks table
            it should require the 'post:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
            or appropriate status code indicating reason for failure
    """
    json_data = request.get_json()

    if not json_data or not json_data.get('title') or not json_data.get('recipe'):
        abort(422)

    recipe = json.dumps(json_data.get('recipe'))
    title = json_data.get('title')

    drink_created = Drink.query.filter_by(title=title).first()
    if drink_created:
        abort(422)

    drink = Drink(title=title, recipe=recipe)
    drink.insert()

    return jsonify({
        "success": True,
        "error": None,
        "message": "Create drink successfully.",
        "drinks": format_drinks_long([drink])
    })


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(payload, drink_id):
    """
    @TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
    """
    json_data = request.get_json()

    if not json_data or not (json_data.get('title') or json_data.get('recipe')):
        abort(422)

    drink = Drink.query.get(drink_id)

    if not drink:
        abort(404)

    title = json_data.get('title')
    if title:
        drink.title = title

    recipe_data = json_data.get('recipe')
    if recipe_data:
        drink.recipe = json.dumps(recipe_data)

    drink.update()

    return jsonify({
        "success": True,
        "error": None,
        "message": "Edit drink successfully.",
        "drinks": format_drinks_long([drink])
    })


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    """
    @TODO implement endpoint
        DELETE /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should delete the corresponding row for <id>
            it should require the 'delete:drinks' permission
        returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
            or appropriate status code indicating reason for failure
    """
    drink = Drink.query.get(drink_id)

    if not drink:
        abort(404)

    drink.delete()

    return jsonify({
        "success": True,
        "error": None,
        "message": "Delete drink successfully.",
        "delete": drink.id
    })


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    print(ex.status_code)
    return jsonify(ex.error), ex.status_code


## Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    print(error)
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(400)
def bad_request(error):
    print(error)
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(401)
def unauthorized(error):
    print(error)
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401


@app.errorhandler(403)
def forbidden(error):
    print(error)
    return jsonify({
        "success": False,
        "error": 403,
        "message": "forbidden"
    }), 403
