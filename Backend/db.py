import pymongo, urllib

# from __main__ import app
from server_entry import app

myclient = None
mydb = None


def login():
    global mydb, myclient
    app.logger.debug("Login")
    username = app.config["DB_USER"]
    password = app.config["DB_PASS"]
    host = app.config["DB_HOST"]
    myclient = pymongo.MongoClient(
        host=host,
        port=27017,
        username=username,
        password=password,
        authSource="admin",
        serverSelectionTimeoutMS=5000,
    )
    try:
        myclient.server_info()
    except pymongo.errors.OperationFailure as e:
        if e.code == 18:
            app.logger.critical("Database authentication Failed")
            exit(0)
        else:
            raise e
    except pymongo.errors.ServerSelectionTimeoutError:
        app.logger.critical("Database unreachable")
        exit(0)
    mydb = myclient["todo-db"]
    # adminsdb = mydb["oscadmins"]
    # if adminsdb.find_one({"username": "admin"}) is None:
    #     adminsdb.insert_one({"username": "admin", "password": "admin"})


# def get_all_todos():
#     todos = mydb["todos"]
#     return todos.find()


def get_all_users():
    usersCol = mydb["users"]
    ret = []
    for user in usersCol.find():
        user["_id"] = str(user["_id"])
        ret.append(user)
    return ret


def check_user(username):
    usersCol = mydb["users"]
    if usersCol.find_one({"username": username}) is not None:
        return True
    return False


def get_user(username):
    usersCol = mydb["users"]
    user = usersCol.find_one({"username": username})
    return user
    # if user is not None:
    #     user["_id"] = str(user["_id"])
    #     return user
    # return None


def delete_user(username):
    usersCol = mydb["users"]
    if check_user(username):
        usersCol.delete_one({"username": username})
        return True
    return False


def create_user(data):
    usersCol = mydb["users"]
    user = usersCol.insert_one(
        {
            "username": data["username"],
            "password": data["password"],
            "token": "",
            "todos": {},
        }
    )
    return user.inserted_id


def update_user(data):
    mycol = mydb["users"]
    mycol.find_one_and_update({"username": data["username"]}, {"$set": data})
