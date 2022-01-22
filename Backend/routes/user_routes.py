# from __main__ import app
from server_entry import app
import db, utils, uuid
from flask import json, request, jsonify, make_response
from routes.security import token_required


@app.route("/users", methods=["GET"])
def get_all_users():
    return make_response(jsonify(db.get_all_users()), 200)


@app.route("/delete-user", methods=["POST"])
def deleteUser():
    jsonData = request.get_json()
    if not jsonData:
        return make_response(jsonify({"error": "No data received"}), 400)
    if not jsonData["username"]:
        return make_response(jsonify({"error": "Missing username"}), 400)
    if not utils.check_types(jsonData):
        return make_response(jsonify({"error": "Invalid data types"}), 400)
    if not db.delete_user(jsonData["username"]):
        return make_response(jsonify({"error": "User does not exist"}), 400)
    return make_response(jsonify({"success": "User deleted"}), 200)


@app.route("/signup", methods=["POST"])
def signup():
    jsonData = request.get_json()
    if not jsonData:
        return make_response(jsonify({"error": "No data received"}), 400)
    if not jsonData["username"] or not jsonData["password"]:
        return make_response(jsonify({"error": "Missing username or password"}), 400)
    if not utils.check_types(jsonData):
        return make_response(jsonify({"error": "Invalid data types"}), 400)
    username = jsonData["username"]
    password = jsonData["password"]
    if utils.check_password(password):
        return make_response(
            jsonify(
                {
                    "error": "Please ensure that password has minimum lenght of 8, at least one uppercase and one Special Chatacter"
                }
            ),
            400,
        )
    encrypted_password = utils.encrypt_password(password)
    if db.check_user(username):
        return make_response(jsonify({"error": "User already exists"}), 400)
    if db.create_user({"username": username, "password": encrypted_password}):
        return make_response(jsonify({"message": "User created"}), 201)
    return make_response(jsonify({"message": "Something went wrong"}), 500)


@app.route("/login", methods=["POST"])
@token_required
def login(user):
    if user:
        return make_response(
            jsonify({"message": "Success", "username": user["username"]}), 200
        )
    if not user:
        jsonData = request.get_json()
        if not jsonData:
            return make_response(jsonify({"error": "No data received"}), 400)
        if not jsonData["username"] or not jsonData["password"]:
            return make_response(
                jsonify({"error": "Missing username or password"}), 400
            )
        if not utils.check_types(jsonData):
            return make_response(jsonify({"error": "Invalid data types"}), 400)
        username = jsonData["username"]
        password = jsonData["password"]
        fetched = db.get_user(username)
        if not fetched:
            return make_response(
                jsonify({"error": "Invalid credentials provided"}), 401
            )
        fetched_password = utils.decrypt_password(fetched["password"])
        if fetched_password != password:
            return make_response(
                jsonify({"error": "Invalid credentials provided"}), 400
            )
        token = utils.generate_token(str(fetched["_id"]), fetched["username"])
        fetched["token"] = token
        # if not db.update_user(fetched):
        #     return make_response(jsonify({"error": "Something went wrong"}), 500)
        db.update_user(fetched)
        return make_response(jsonify({"token": token, "username": username}), 200)


@app.route("/todos", methods=["GET"])
@token_required
def getTodos(user):
    if not user:
        return make_response(jsonify({"message": "User unauthorized"}), 401)
    return make_response(
        jsonify({"message": "Success", "todos": list(user["todos"].values())}),
        200
        # jsonify({"message": "Success", "todos": user["todos"]}),
    )


@app.route("/add-todo", methods=["POST"])
@token_required
def addTodo(user):
    if not user:
        return make_response(jsonify({"message": "User unauthorized"}), 401)
    jsonData = request.get_json()
    if not jsonData:
        return make_response(jsonify({"error": "No data received"}), 400)
    if not jsonData["title"] or not jsonData["description"] or not jsonData["expiry"]:
        return make_response(
            jsonify({"error": "Missing title, description or expiry"}), 400
        )
    if not utils.check_types(jsonData):
        return make_response(jsonify({"error": "Invalid data types"}), 400)
    id = str(uuid.uuid4())
    while id in user["todos"]:
        id = str(uuid.uuid4())
    todo = {
        "id": id,
        "title": jsonData["title"],
        "description": jsonData["description"],
        "expiry": jsonData["expiry"],
        "completed": False,
    }
    user["todos"][id] = todo
    db.update_user(user)
    return make_response(jsonify({"message": "Todo added Successfully", "id": id}), 200)


# @app.route("/add-todo", methods=["POST"])
# @token_required
# def addTodo(user):
#     if not user:
#         return make_response(jsonify({"message": "User unauthorized"}), 401)
#     jsonData = request.get_json()
#     if not jsonData:
#         return make_response(jsonify({"error": "No data received"}), 400)
#     if not jsonData["title"] or not jsonData["description"] or not jsonData["expiry"]:
#         return make_response(
#             jsonify({"error": "Missing title, description or expiry"}), 400
#         )
#     if not utils.check_types(jsonData):
#         return make_response(jsonify({"error": "Invalid data types"}), 400)
#     id = str(uuid.uuid4())
#     while id in user["todos"]:
#         id = str(uuid.uuid4())
#     todo = {
#         "id": id,
#         "title": jsonData["title"],
#         "description": jsonData["description"],
#         "expiry": jsonData["expiry"],
#         "completed": False,
#     }
#     user["todos"][id] = todo
#     db.update_user(user)
#     return make_response(jsonify({"message": "Todo added Successfully"}), 200)


@app.route("/update-todo", methods=["POST"])
@token_required
def updateTodo(user):
    if not user:
        return make_response(jsonify({"message": "User unauthorized"}), 401)
    jsonData = request.get_json()
    if not jsonData:
        return make_response(jsonify({"error": "No data received"}), 400)
    if not jsonData["todo"]:
        return make_response(jsonify({"error": "Missing data"}), 400)
    if not utils.check_types(jsonData):
        return make_response(jsonify({"error": "Invalid data types"}), 400)
    todo = jsonData["todo"]
    if todo["id"] not in user["todos"]:
        return make_response(jsonify({"error": "Invalid data"}), 400)
    user["todos"][todo["id"]] = todo
    db.update_user(user)
    return make_response(jsonify({"message": "Todo updated Successfully"}), 200)


@app.route("/delete-todo", methods=["POST"])
@token_required
def deleteTodo(user):
    if not user:
        return make_response(jsonify({"message": "User unauthorized"}), 401)
    jsonData = request.get_json()
    if not jsonData:
        return make_response(jsonify({"error": "No data received"}), 400)
    if not jsonData["id"]:
        return make_response(jsonify({"error": "Missing data"}), 400)
    if not utils.check_types(jsonData):
        return make_response(jsonify({"error": "Invalid data types"}), 400)
    del user["todos"][jsonData["id"]]
    db.update_user(user)
    return make_response(jsonify({"message": "Todo Deleted Successfully"}), 200)
