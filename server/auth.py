from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from marshmallow import ValidationError

from .extensions import db
from .models import User
from .schemas import LoginSchema, SignupSchema, UserSchema


auth_bp = Blueprint("auth", __name__)

user_schema = UserSchema()
signup_schema = SignupSchema()
login_schema = LoginSchema()


@auth_bp.post("/signup")
def signup():
    data = request.get_json(silent=True) or {}

    try:
        user_data = signup_schema.load(data)
    except ValidationError as error:
        return {"errors": error.messages}, 400

    existing_user = User.query.filter_by(
        username=user_data["username"]
    ).first()

    if existing_user:
        return {"error": "Username already exists"}, 409

    user = User(username=user_data["username"])
    user.set_password(user_data["password"])

    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=str(user.id))

    return {
        "token": access_token,
        "user": user_schema.dump(user),
    }, 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}

    try:
        login_data = login_schema.load(data)
    except ValidationError as error:
        return {"errors": error.messages}, 400

    user = User.query.filter_by(
        username=login_data["username"]
    ).first()

    if not user or not user.check_password(login_data["password"]):
        return {"error": "Invalid username or password"}, 401

    access_token = create_access_token(identity=str(user.id))

    return {
        "token": access_token,
        "user": user_schema.dump(user),
    }, 200


@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()

    user = db.session.get(User, int(user_id))

    if not user:
        return {"error": "User not found"}, 404

    return user_schema.dump(user), 200
