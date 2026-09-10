import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest

from server.app import create_app
from server.extensions import db
from server.models import User


@pytest.fixture()
def client():
    app = create_app()

    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        JWT_SECRET_KEY="test-secret-key-that-is-at-least-32-characters",
    )

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def signup(client, username, password="password123"):
    return client.post(
        "/signup",
        json={
            "username": username,
            "password": password,
            "password_confirmation": password,
        },
    )


def login(client, username, password="password123"):
    response = client.post(
        "/login",
        json={
            "username": username,
            "password": password,
        },
    )

    if response.status_code != 200:
        return response, {}

    token = response.get_json()["token"]

    return response, {
        "Authorization": f"Bearer {token}",
    }


def create_note(
    client,
    headers,
    title="Test Note",
    content="Test content",
    category="testing",
):
    return client.post(
        "/notes",
        headers=headers,
        json={
            "title": title,
            "content": content,
            "category": category,
        },
    )


# -------------------------
# Authentication tests
# -------------------------


def test_signup_creates_user(client):
    response = signup(client, "Tabby")

    assert response.status_code == 201
    assert response.get_json()["user"]["username"] == "Tabby"


def test_signup_hashes_password(client):
    signup(client, "Tabby")

    user = User.query.filter_by(username="Tabby").first()

    assert user is not None
    assert user.password_hash != "password123"
    assert user.password_hash.startswith("$2")


def test_duplicate_signup_returns_conflict(client):
    signup(client, "Tabby")

    response = signup(client, "Tabby")

    assert response.status_code == 409


def test_signup_rejects_mismatched_passwords(client):
    response = client.post(
        "/signup",
        json={
            "username": "Tabby",
            "password": "password123",
            "password_confirmation": "different123",
        },
    )

    assert response.status_code == 400


def test_login_returns_jwt(client):
    signup(client, "Tabby")

    response, headers = login(client, "Tabby")

    assert response.status_code == 200
    assert "token" in response.get_json()
    assert headers["Authorization"].startswith("Bearer ")


def test_invalid_login_returns_unauthorized(client):
    signup(client, "Tabby")

    response, headers = login(
        client,
        "Tabby",
        "wrong-password",
    )

    assert response.status_code == 401
    assert headers == {}


def test_me_requires_authentication(client):
    response = client.get("/me")

    assert response.status_code == 401


def test_me_returns_authenticated_user(client):
    signup(client, "Tabby")

    _, headers = login(client, "Tabby")

    response = client.get(
        "/me",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.get_json()["username"] == "Tabby"


# -------------------------
# Notes authentication
# -------------------------


def test_notes_require_authentication(client):
    response = client.get("/notes")

    assert response.status_code == 401


# -------------------------
# Notes CRUD
# -------------------------


def test_create_note(client):
    signup(client, "Tabby")

    _, headers = login(client, "Tabby")

    response = create_note(
        client,
        headers,
        title="My First Note",
        content="Important content",
        category="work",
    )

    assert response.status_code == 201

    note = response.get_json()

    assert note["title"] == "My First Note"
    assert note["content"] == "Important content"
    assert note["category"] == "work"
    assert note["user_id"] is not None
    assert "created_at" in note
    assert "updated_at" in note
    assert note["user"]["username"] == "Tabby"


def test_create_note_requires_category(client):
    signup(client, "Tabby")

    _, headers = login(client, "Tabby")

    response = client.post(
        "/notes",
        headers=headers,
        json={
            "title": "No Category",
            "content": "This should fail",
        },
    )

    assert response.status_code == 400


def test_get_single_note(client):
    signup(client, "Tabby")

    _, headers = login(client, "Tabby")

    created = create_note(client, headers)
    note_id = created.get_json()["id"]

    response = client.get(
        f"/notes/{note_id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.get_json()["id"] == note_id


def test_update_note(client):
    signup(client, "Tabby")

    _, headers = login(client, "Tabby")

    created = create_note(client, headers)
    note_id = created.get_json()["id"]

    response = client.patch(
        f"/notes/{note_id}",
        headers=headers,
        json={
            "title": "Updated Title",
            "category": "updated",
        },
    )

    assert response.status_code == 200

    note = response.get_json()

    assert note["title"] == "Updated Title"
    assert note["category"] == "updated"


def test_update_note_rejects_empty_payload(client):
    signup(client, "Tabby")

    _, headers = login(client, "Tabby")

    created = create_note(client, headers)
    note_id = created.get_json()["id"]

    response = client.patch(
        f"/notes/{note_id}",
        headers=headers,
        json={},
    )

    assert response.status_code == 400


def test_update_note_rejects_blank_values(client):
    signup(client, "Tabby")

    _, headers = login(client, "Tabby")

    created = create_note(client, headers)
    note_id = created.get_json()["id"]

    response = client.patch(
        f"/notes/{note_id}",
        headers=headers,
        json={
            "title": "   ",
        },
    )

    assert response.status_code == 400


def test_delete_note(client):
    signup(client, "Tabby")

    _, headers = login(client, "Tabby")

    created = create_note(client, headers)
    note_id = created.get_json()["id"]

    response = client.delete(
        f"/notes/{note_id}",
        headers=headers,
    )

    assert response.status_code == 200

    missing = client.get(
        f"/notes/{note_id}",
        headers=headers,
    )

    assert missing.status_code == 404


# -------------------------
# Authorization / ownership
# -------------------------


def test_other_user_cannot_access_note(client):
    signup(client, "Tabby")
    _, tabby_headers = login(client, "Tabby")

    signup(client, "Prince")
    _, prince_headers = login(client, "Prince")

    created = create_note(
        client,
        tabby_headers,
        title="Private Note",
        content="Tabby's private content",
        category="private",
    )

    note_id = created.get_json()["id"]

    response = client.get(
        f"/notes/{note_id}",
        headers=prince_headers,
    )

    assert response.status_code == 403


def test_other_user_cannot_update_note(client):
    signup(client, "Tabby")
    _, tabby_headers = login(client, "Tabby")

    signup(client, "Prince")
    _, prince_headers = login(client, "Prince")

    created = create_note(
        client,
        tabby_headers,
        title="Private Note",
    )

    note_id = created.get_json()["id"]

    response = client.patch(
        f"/notes/{note_id}",
        headers=prince_headers,
        json={
            "title": "Unauthorized Update",
        },
    )

    assert response.status_code == 403


def test_other_user_cannot_delete_note(client):
    signup(client, "Tabby")
    _, tabby_headers = login(client, "Tabby")

    signup(client, "Prince")
    _, prince_headers = login(client, "Prince")

    created = create_note(
        client,
        tabby_headers,
        title="Private Note",
    )

    note_id = created.get_json()["id"]

    response = client.delete(
        f"/notes/{note_id}",
        headers=prince_headers,
    )

    assert response.status_code == 403


def test_user_only_sees_their_own_notes(client):
    signup(client, "Tabby")
    _, tabby_headers = login(client, "Tabby")

    signup(client, "Prince")
    _, prince_headers = login(client, "Prince")

    create_note(
        client,
        tabby_headers,
        title="Tabby's Note",
    )

    create_note(
        client,
        prince_headers,
        title="Prince's Note",
    )

    tabby_notes = client.get(
        "/notes",
        headers=tabby_headers,
    ).get_json()["notes"]

    prince_notes = client.get(
        "/notes",
        headers=prince_headers,
    ).get_json()["notes"]

    assert len(tabby_notes) == 1
    assert tabby_notes[0]["title"] == "Tabby's Note"

    assert len(prince_notes) == 1
    assert prince_notes[0]["title"] == "Prince's Note"


# -------------------------
# Pagination
# -------------------------


def test_notes_are_paginated(client):
    signup(client, "Tabby")

    _, headers = login(client, "Tabby")

    for number in range(5):
        response = create_note(
            client,
            headers,
            title=f"Note {number}",
            content=f"Content {number}",
            category="testing",
        )

        assert response.status_code == 201

    page_one = client.get(
        "/notes?page=1&per_page=2",
        headers=headers,
    )

    assert page_one.status_code == 200

    page_one_data = page_one.get_json()

    assert len(page_one_data["notes"]) == 2
    assert page_one_data["pagination"]["page"] == 1
    assert page_one_data["pagination"]["pages"] == 3
    assert page_one_data["pagination"]["total"] == 5
    assert page_one_data["pagination"]["has_next"] is True
    assert page_one_data["pagination"]["has_prev"] is False

    page_two = client.get(
        "/notes?page=2&per_page=2",
        headers=headers,
    )

    assert page_two.status_code == 200

    page_two_data = page_two.get_json()

    assert len(page_two_data["notes"]) == 2
    assert page_two_data["pagination"]["page"] == 2
    assert page_two_data["pagination"]["has_next"] is True
    assert page_two_data["pagination"]["has_prev"] is True

    page_three = client.get(
        "/notes?page=3&per_page=2",
        headers=headers,
    )

    assert page_three.status_code == 200

    page_three_data = page_three.get_json()

    assert len(page_three_data["notes"]) == 1
    assert page_three_data["pagination"]["page"] == 3
    assert page_three_data["pagination"]["has_next"] is False
    assert page_three_data["pagination"]["has_prev"] is True


def test_invalid_pagination_returns_bad_request(client):
    signup(client, "Tabby")

    _, headers = login(client, "Tabby")

    response = client.get(
        "/notes?page=0",
        headers=headers,
    )

    assert response.status_code == 400

    response = client.get(
        "/notes?per_page=101",
        headers=headers,
    )

    assert response.status_code == 400


# -------------------------
# 404 handling
# -------------------------


def test_missing_note_returns_not_found(client):
    signup(client, "Tabby")

    _, headers = login(client, "Tabby")

    response = client.get(
        "/notes/9999",
        headers=headers,
    )

    assert response.status_code == 404


def test_update_missing_note_returns_not_found(client):
    signup(client, "Tabby")

    _, headers = login(client, "Tabby")

    response = client.patch(
        "/notes/9999",
        headers=headers,
        json={
            "title": "Does not exist",
        },
    )

    assert response.status_code == 404


def test_delete_missing_note_returns_not_found(client):
    signup(client, "Tabby")

    _, headers = login(client, "Tabby")

    response = client.delete(
        "/notes/9999",
        headers=headers,
    )

    assert response.status_code == 404
