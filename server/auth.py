from flask import Blueprint, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from .extensions import db
from .models import User
auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/signup")
def signup():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")
    password_confirmation = data.get("password_confirmation")

    if not username or not password or not password_confirmation:
        return {"error": "Username, password, and password confirmation are required"}, 400

    if password != password_confirmation:
        return {"error": "Passwords do not match"}, 400

    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        return {"error": "Username already exists"}, 409

    user = User(username=username)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=str(user.id))

    return {
        "token": access_token,
        "user": {
            "id": user.id,
            "username": user.username
        }
    }, 201



@auth_bp.post("/login")
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {"error": "Username and password are required"}, 400

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return {"error": "Invalid username or password"}, 401

    access_token = create_access_token(identity=str(user.id))

    return {
        "token": access_token,
        "user": {
            "id": user.id,
            "username": user.username
        }
    }, 200



@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()

    user = User.query.get(int(user_id))

    if not user:
        return {"error": "User not found"}, 404

    return {
        "id": user.id,
        "username": user.username
    }, 200
