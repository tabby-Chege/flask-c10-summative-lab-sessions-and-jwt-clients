from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from .extensions import db
from .models import Note

notes_bp = Blueprint("notes", __name__)


def serialize_note(note):
    return {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "user_id": note.user_id,
    }


def parse_pagination():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    if page is None or page < 1:
        page = 1
    if per_page is None or per_page < 1:
        per_page = 10
    if per_page > 100:
        per_page = 100

    return page, per_page


@notes_bp.get("/notes")
@jwt_required()
def get_notes():
    user_id = int(get_jwt_identity())
    page, per_page = parse_pagination()

    query = Note.query.filter_by(user_id=user_id).order_by(Note.id.desc())
    items = query.paginate(page=page, per_page=per_page, error_out=False)

    return {
        "notes": [serialize_note(note) for note in items.items],
        "page": page,
        "per_page": per_page,
        "total": items.total,
    }, 200


@notes_bp.get("/notes/<int:id>")
@jwt_required()
def get_note(id):
    user_id = int(get_jwt_identity())
    note = Note.query.filter_by(id=id, user_id=user_id).first()

    if not note:
        return {"error": "Note not found"}, 404

    return serialize_note(note), 200


@notes_bp.post("/notes")
@jwt_required()
def create_note():
    data = request.get_json() or {}
    title = data.get("title")
    content = data.get("content")

    if not title or not str(title).strip():
        return {"error": "Title is required"}, 400

    if not content or not str(content).strip():
        return {"error": "Content is required"}, 400

    user_id = int(get_jwt_identity())
    note = Note(title=str(title).strip(), content=str(content).strip(), user_id=user_id)

    db.session.add(note)
    db.session.commit()

    return serialize_note(note), 201


@notes_bp.patch("/notes/<int:id>")
@jwt_required()
def update_note(id):
    data = request.get_json() or {}
    user_id = int(get_jwt_identity())
    note = Note.query.filter_by(id=id, user_id=user_id).first()

    if not note:
        return {"error": "Note not found"}, 404

    if "title" in data and (not data.get("title") or not str(data.get("title")).strip()):
        return {"error": "Title cannot be empty"}, 400

    if "content" in data and (not data.get("content") or not str(data.get("content")).strip()):
        return {"error": "Content cannot be empty"}, 400

    if "title" in data:
        note.title = str(data.get("title")).strip()
    if "content" in data:
        note.content = str(data.get("content")).strip()

    db.session.commit()

    return serialize_note(note), 200


@notes_bp.delete("/notes/<int:id>")
@jwt_required()
def delete_note(id):
    user_id = int(get_jwt_identity())
    note = Note.query.filter_by(id=id, user_id=user_id).first()

    if not note:
        return {"error": "Note not found"}, 404

    db.session.delete(note)
    db.session.commit()

    return {"message": "Note deleted", "id": id}, 200
