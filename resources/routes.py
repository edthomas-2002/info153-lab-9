from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import db
from models import UserModel
from schemas import UserSchema, UserCreateSchema
from flask import request, jsonify

from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt

# blue print divides data into multiple segments
blp = Blueprint("routes", __name__, description="Routes")

@blp.route("/register", methods=['POST'])
@blp.arguments(UserCreateSchema)
def register(user_data):
    if UserModel.query.filter( UserModel.username == user_data["username"]).first(): 
        abort(409, message="A user with that username or email already exists.")

    user_data["password"] = pbkdf2_sha256.hash(user_data["password"])
    new_user = UserModel(**user_data)
    db.session.add(new_user)
    db.session.commit()
    return {"Message": f"Successfully created user {new_user.username}"}, 200

@blp.route("/login", methods=['POST'])
@blp.arguments(UserSchema)
def login(user_data):
    user = UserModel.query.filter(
        UserModel.username == user_data["username"]
    ).first()

    if user and pbkdf2_sha256.verify(user_data["password"], user.password):
        access_token = create_access_token(identity=user.id, fresh=True)
        # refresh_token = create_refresh_token(identity=user.id)
        return {"access_token": access_token}
    
    abort(401, message="Invalid creds")

@blp.route("/refresh", methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    # Make fresh false for this refreshed access token
    # -- do not want user to have full privileges until they reauthenticate
    new_token = create_access_token(identity=current_user, fresh=False)
    return {"access_token": new_token}


@blp.route("/protected", methods=['GET'])
@jwt_required() # if need a fresh token, say fresh=True
def protected():
    jwt = get_jwt()
    user_id = jwt["sub"]
    user = UserModel.query.filter(
        UserModel.id == user_id
    ).first()

    return {"username":user.username, "quote": user.quote}