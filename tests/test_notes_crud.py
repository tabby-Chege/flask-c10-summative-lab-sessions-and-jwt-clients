import pytest

from server.app import create_app
from server.extensions import db


def test_notes_crud_endpoints_protected_and_behave():
    app = create_app()
    app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI="sqlite:///:memory:")

    with app.app_context():
        db.drop_all()
        db.create_all()

    client = app.test_client()

    signup = client.post(
        "/signup",
        json={
            "username": "alice",
            "password": "secret123",
            "password_confirmation": "secret123",
        },
    )

    assert signup.status_code == 201, signup.get_data(as_text=True)
    token = signup.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    create = client.post(
        "/notes",
        json={"title": "First", "content": "Write down something"},
        headers=headers,
    )
    assert create.status_code == 201, create.get_data(as_text=True)
    created = create.get_json()
    note_id = created["id"]

    listed = client.get("/notes", headers=headers)
    assert listed.status_code == 200, listed.get_data(as_text=True)
    listed_json = listed.get_json()
    assert listed_json["notes"] and listed_json["notes"][0]["title"] == "First"

    update = client.patch(
        f"/notes/{note_id}",
        json={"title": "Updated title"},
        headers=headers,
    )
    assert update.status_code == 200, update.get_data(as_text=True)
    updated = update.get_json()
    assert updated["title"] == "Updated title"

    delete_resp = client.delete(f"/notes/{note_id}", headers=headers)
    assert delete_resp.status_code == 200, delete_resp.get_data(as_text=True)

    forbidden = client.get("/notes")
    assert forbidden.status_code == 401
