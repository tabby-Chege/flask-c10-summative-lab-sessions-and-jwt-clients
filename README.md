# Secure Flask Notes API

## Description

This project is a backend REST API built with Flask for managing personal notes.

Users can create an account, log in, and use a JWT token to access their notes. Each user can create, view, update, and delete their own notes. A user cannot access another user's notes.

The project also includes password hashing, Marshmallow validation and serialization, SQLAlchemy relationships, database migrations, pagination, seeding, and automated tests.

## Features

* User registration and login
* JWT authentication
* Password hashing using Flask-Bcrypt
* Protected API routes
* Notes CRUD operations
* User ownership and authorization
* Marshmallow validation and serialization
* Nested user information in note responses
* Pagination for notes
* SQLAlchemy user-note relationship
* Flask-Migrate database migrations
* Database seed data
* Automated tests with pytest

## Technologies Used

* Python 3.12
* Flask
* Flask-SQLAlchemy
* Flask-Migrate
* Flask-Bcrypt
* Flask-JWT-Extended
* Marshmallow
* SQLite
* Pytest
* Pipenv

## Project Structure

```text
.
├── client-with-jwt/
├── client-with-sessions/
├── migrations/
│   └── versions/
│       ├── 3baf022ae864_create_users_table.py
│       ├── 7c9c8fd9d2b1_create_notes_table.py
│       └── 2d5f5c021a41_add_category_to_notes.py
├── server/
│   ├── __init__.py
│   ├── app.py
│   ├── auth.py
│   ├── config.py
│   ├── extensions.py
│   ├── models.py
│   ├── notes.py
│   └── schemas.py
├── tests/
│   └── test_api.py
├── Pipfile
├── Pipfile.lock
├── README.md
├── run.py
└── seed.py
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone git@github.com:tabby-Chege/flask-c10-summative-lab-sessions-and-jwt-clients.git
cd flask-c10-summative-lab-sessions-and-jwt-clients
```

### 2. Install dependencies

This project uses Pipenv.

```bash
pipenv install
pipenv install --dev
```

Activate the virtual environment:

```bash
pipenv shell
```

### 3. Environment Variables

The application supports environment variables for the JWT secret and database URL.

For local development, you can use:

```bash
export JWT_SECRET_KEY="replace-with-a-long-random-secret"
export DATABASE_URL="sqlite:///notes.db"
```

The `.env` file is included in `.gitignore` so secrets are not committed to GitHub.

### 4. Run Database Migrations

Apply the existing migrations with:

```bash
pipenv run flask --app run.py db upgrade
```

You can check the current migration:

```bash
pipenv run flask --app run.py db current
```

To see the migration history:

```bash
pipenv run flask --app run.py db history
```

The migrations create the users table, notes table, and category field for notes.

### 5. Seed the Database

Run:

```bash
pipenv run python seed.py
```

The seed script creates sample users and notes for testing.

The seed script can be run more than once without creating duplicate seed records.

### 6. Start the API

Run:

```bash
pipenv run python run.py
```

The API will be available at:

```text
http://127.0.0.1:5555
```

The root endpoint can be used to check that the API is running:

```text
GET /
```

## Authentication

The API uses **JWT authentication**.

There is only one authentication method used in this project: JWT.

After registering or logging in, the API returns an access token. Protected requests should include the token in the `Authorization` header:

```text
Authorization: Bearer <your-token>
```

### Register a User

```text
POST /signup
```

Example request:

```json
{
    "username": "Tabby",
    "password": "password123",
    "password_confirmation": "password123"
}
```

A successful registration returns `201 Created` and includes the new user's information and JWT token.

### Login

```text
POST /login
```

Example request:

```json
{
    "username": "Tabby",
    "password": "password123"
}
```

A successful login returns `200 OK` and provides a JWT token.

### Get Current User

```text
GET /me
```

This route is protected and requires a valid JWT.

Example header:

```text
Authorization: Bearer <your-token>
```

The endpoint returns information about the user associated with the token.

## Notes API

All Notes endpoints are protected and require a valid JWT.

A note contains:

* `id`
* `title`
* `content`
* `category`
* `user_id`
* `created_at`
* `updated_at`

The `user_id` connects each note to the user who owns it.

### Create a Note

```text
POST /notes
```

Example request:

```json
{
    "title": "Study Notes",
    "content": "Review Flask and SQLAlchemy.",
    "category": "school"
}
```

A successful request returns `201 Created`.

The `user_id` is taken from the logged-in user's JWT instead of being supplied by the client.

### Get Notes

```text
GET /notes
```

This returns the notes belonging to the currently authenticated user.

Example:

```text
GET /notes?page=1&per_page=10
```

The response includes the notes and pagination information.

Example response structure:

```json
{
    "notes": [],
    "pagination": {
        "page": 1,
        "per_page": 10,
        "pages": 1,
        "total": 0,
        "has_next": false,
        "has_prev": false
    }
}
```

### Get One Note

```text
GET /notes/<id>
```

Example:

```text
GET /notes/1
```

The endpoint checks that the note exists and that it belongs to the authenticated user.

### Update a Note

```text
PATCH /notes/<id>
```

Example request:

```json
{
    "title": "Updated Study Notes",
    "category": "school"
}
```

Only the fields that need to be changed have to be included.

The endpoint checks note ownership before making the update.

A successful update returns `200 OK`.

### Delete a Note

```text
DELETE /notes/<id>
```

Example:

```text
DELETE /notes/1
```

The endpoint checks ownership before deleting the note.

A successful deletion returns `200 OK`.

## Pagination

The notes list supports pagination using query parameters.

Example:

```text
GET /notes?page=1&per_page=2
```

Another page can be requested with:

```text
GET /notes?page=2&per_page=2
```

The response includes:

* current page
* number of items per page
* total number of pages
* total number of notes
* whether there is a next page
* whether there is a previous page

The API also validates the pagination values. Page numbers must be at least `1`, and `per_page` must be between `1` and `100`.

## Authorization and Ownership

Authentication answers:

> Who is making this request?

Authorization answers:

> Does this user have permission to access this resource?

For this project, the authenticated user's ID comes from the JWT.

When accessing an individual note, the API checks the note's `user_id` against the current user's ID.

A user can therefore only access their own notes.

For example, if User A tries to view, update, or delete a note owned by User B, the API returns:

```text
403 Forbidden
```

This ownership check is done on the individual note routes and prevents users from changing another user's data.

## Password Security

Passwords are not stored as plain text.

The project uses Flask-Bcrypt to generate a password hash when a user registers.

During login, the submitted password is checked against the stored hash.

Only the password hash is stored in the database.

## Marshmallow

Marshmallow is used for validation, serialization, and deserialization.

The project includes schemas for users, authentication requests, and notes.

For example, note data is loaded through Marshmallow before a note is created or updated:

```python
note_data = note_schema.load(data)
```

Notes are serialized when returned by the API:

```python
note_schema.dump(note)
```

The note schema also includes nested user information when a note is serialized.

Fields such as `user_id`, `created_at`, and `updated_at` are controlled by the API rather than being supplied by the client.

## Database Relationships

A user can have many notes, while each note belongs to one user.

The relationship is represented using SQLAlchemy:

```text
User
  |
  | one-to-many
  |
  └── Note
```

The `notes` table contains a `user_id` foreign key that references the `users` table.

## HTTP Status Codes

The API uses HTTP status codes to show the result of requests.

| Status | Meaning                                              |
| ------ | ---------------------------------------------------- |
| 200    | Request successful                                   |
| 201    | Resource created                                     |
| 400    | Invalid request or validation error                  |
| 401    | Authentication required or invalid credentials/token |
| 403    | Authenticated user does not have permission          |
| 404    | Resource was not found                               |
| 409    | Username already exists                              |

## Testing

The project includes automated tests using pytest.

Run the tests with:

```bash
pipenv run python -m pytest -q
```

The test suite covers authentication, protected routes, note CRUD operations, validation, authorization, ownership checks, and pagination.

The project also tests the API using more than one user to make sure one user cannot access another user's notes.

## Git and Team Collaboration

The project was developed as a group using Git and GitHub.

Different parts of the project were worked on through feature branches, including:

* JWT authentication
* Notes CRUD and authorization
* Pagination, seeding, and testing
* Documentation

The final backend combines these parts into one Flask API.

## Project Goal

The main goal of the project was to build a working Flask backend that demonstrates authentication, authorization, database relationships, CRUD operations, validation, pagination, and secure handling of user data.

The project focuses on making sure that a request is not only authenticated, but also checked for the correct user's permission before accessing their notes.
