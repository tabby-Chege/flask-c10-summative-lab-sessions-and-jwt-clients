from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .extensions import db
from .models import Note

notes_bp = Blueprint("notes", __name__, url_prefix="/notes")

@notes_bp.route("", methods=["GET"])
@jwt_required()
def get_notes():
    user_id = int(get_jwt_identity())
    
    # Query parameters for pagination
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    # Restrict query strictly to logged-in user's notes
    pagination = Note.query.filter_by(user_id=user_id).order_by(Note.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    notes = pagination.items

    return {
        "notes": [
            {
                "id": note.id,
                "title": note.title,
                "content": note.content,
                "created_at": note.created_at.isoformat() if note.created_at else None,
                "user_id": note.user_id
            } for note in notes
        ],
        "pagination": {
            "total": pagination.total,
            "pages": pagination.pages,
            "page": page,
            "per_page": per_page,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
        }
    }, 200


@notes_bp.route("", methods=["POST"])
@jwt_required()
def create_note():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    title = data.get("title")
    content = data.get("content")

    if not title or not content:
        return {"error": "Title and content are required fields"}, 400

    note = Note(title=title, content=content, user_id=user_id)
    db.session.add(note)
    db.session.commit()

    return {
        "message": "Note created successfully",
        "note": {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "created_at": note.created_at.isoformat() if note.created_at else None,
            "user_id": note.user_id
        }
    }, 201


@notes_bp.route("/<int:id>", methods=["PATCH"])
@jwt_required()
def update_note(id):
    user_id = int(get_jwt_identity())
    note = Note.query.get(id)

    if not note:
        return {"error": "Note not found"}, 404

    # Authorization Check
    if note.user_id != user_id:
        return {"error": "Unauthorized to edit this note"}, 403

    data = request.get_json() or {}
    if "title" in data:
        note.title = data["title"]
    if "content" in data:
        note.content = data["content"]

    db.session.commit()

    return {
        "message": "Note updated successfully",
        "note": {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "user_id": note.user_id
        }
    }, 200


@notes_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_note(id):
    user_id = int(get_jwt_identity())
    note = Note.query.get(id)

    if not note:
        return {"error": "Note not found"}, 404

    # Authorization Check
    if note.user_id != user_id:
        return {"error": "Unauthorized to delete this note"}, 403

    db.session.delete(note)
    db.session.commit()

    return {"message": "Note deleted successfully"}, 200