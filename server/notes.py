from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError

from .extensions import db
from .models import Note
from .schemas import NoteSchema


notes_bp = Blueprint("notes", __name__)

note_schema = NoteSchema()
notes_schema = NoteSchema(many=True)


def _current_user_id():
    return int(get_jwt_identity())


@notes_bp.get("/notes")
@jwt_required()
def list_notes():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    if page < 1:
        return {"error": "page must be at least 1"}, 400

    if per_page < 1 or per_page > 100:
        return {"error": "per_page must be between 1 and 100"}, 400

    pagination = (
        Note.query.filter_by(user_id=_current_user_id())
        .order_by(Note.created_at.desc())
        .paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )
    )

    return {
        "notes": notes_schema.dump(pagination.items),
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "pages": pagination.pages,
            "total": pagination.total,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        },
    }, 200


@notes_bp.post("/notes")
@jwt_required()
def create_note():
    data = request.get_json(silent=True) or {}

    try:
        note_data = note_schema.load(data)
    except ValidationError as error:
        return {"errors": error.messages}, 400

    note = Note(
        title=note_data["title"].strip(),
        content=note_data["content"].strip(),
        category=note_data["category"].strip(),
        user_id=_current_user_id(),
    )

    db.session.add(note)
    db.session.commit()

    return note_schema.dump(note), 201


@notes_bp.get("/notes/<int:note_id>")
@jwt_required()
def get_note(note_id):
    note = db.session.get(Note, note_id)

    if not note:
        return {"error": "Note not found"}, 404

    if note.user_id != _current_user_id():
        return {"error": "Forbidden"}, 403

    return note_schema.dump(note), 200


@notes_bp.patch("/notes/<int:note_id>")
@jwt_required()
def update_note(note_id):
    note = db.session.get(Note, note_id)

    if not note:
        return {"error": "Note not found"}, 404

    if note.user_id != _current_user_id():
        return {"error": "Forbidden"}, 403

    data = request.get_json(silent=True) or {}

    if not data:
        return {"error": "At least one field is required"}, 400

    try:
        note_data = NoteSchema(partial=True).load(data)
    except ValidationError as error:
        return {"errors": error.messages}, 400

    if "title" in note_data:
        note.title = note_data["title"].strip()

    if "content" in note_data:
        note.content = note_data["content"].strip()

    if "category" in note_data:
        note.category = note_data["category"].strip()

    db.session.commit()

    return note_schema.dump(note), 200


@notes_bp.delete("/notes/<int:note_id>")
@jwt_required()
def delete_note(note_id):
    note = db.session.get(Note, note_id)

    if not note:
        return {"error": "Note not found"}, 404

    if note.user_id != _current_user_id():
        return {"error": "Forbidden"}, 403

    db.session.delete(note)
    db.session.commit()

    return {"message": "Note deleted successfully"}, 200
