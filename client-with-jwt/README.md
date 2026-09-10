# Secure Notes API

A Flask REST API for a productivity application with user authentication, JWT authorization, and personal note management.

## Overview

This project is a secure backend API for managing user-specific notes.

It includes:

- User registration and login
- JWT-based authentication
- Password hashing
- Protected note routes
- Note creation, reading, updating, and deletion
- Pagination for note retrieval
- Database migrations and seeding
- Automated tests

---

## Features

- Secure user authentication with Flask-JWT-Extended
- Password hashing with Flask-Bcrypt
- Notes are restricted to their owners only
- API responses include clear HTTP status codes
- Database support with SQLite and Flask-SQLAlchemy
- Test suite for auth, notes, authorization, and pagination

---

## Prerequisites

Before starting, make sure you have:

- Python 3.12+
- pip
- Git
- A terminal or command prompt

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/tabby-Chege/flask-c10-summative-lab-sessions-and-jwt-clients
cd flask-c10-summative-lab-sessions-and-jwt-clients
```

### 2. Create and activate a virtual environment

On Linux or macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install project dependencies

```bash
pip install -r requirements.txt
```

### 4. Set the JWT secret key

Create a secure secret key for the application:

```bash
export JWT_SECRET_KEY="your-secure-secret-key"
```

If you are using Windows PowerShell, use:

```powershell
$env:JWT_SECRET_KEY="your-secure-secret-key"
```

---

## Database Setup

### 1. Initialize migrations (only if needed)

```bash
flask --app app db init
```

### 2. Generate migration files

```bash
flask --app app db migrate -m "Create users and notes tables"
```

### 3. Apply the migrations

```bash
flask --app app db upgrade
```

### 4. Seed the database

```bash
python seed.py
```

This adds sample users and notes for testing.

> Default seeded password: `password123`

---

## Run the Application

### Option 1: Run directly with Python

```bash
python app.py
```

### Option 2: Run with Flask CLI

```bash
flask --app app run
```

The API will be available at:

```text
http://127.0.0.1:5000
```

---

## API Endpoints

### Authentication

- `POST /signup`
  - Register a new user account

- `POST /login`
  - Log in and receive a JWT access token

- `GET /me`
  - Get the current authenticated user
  - Requires a valid JWT

### Notes

- `GET /notes`
  - Get the logged-in user's notes
  - Supports `page` and `per_page` query parameters
  - Requires a valid JWT

- `POST /notes`
  - Create a new note for the logged-in user
  - Requires a valid JWT

- `GET /notes/<id>`
  - Get one note by ID
  - Requires a valid JWT

- `PATCH /notes/<id>`
  - Update an owned note
  - Requires a valid JWT

- `DELETE /notes/<id>`
  - Delete an owned note
  - Requires a valid JWT

---

## Security Rules

- Users can only view, update, or delete their own notes
- Attempting to access another user's note returns `403 Forbidden`
- Logout is handled on the client side by deleting the stored JWT token

---

## HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid input or bad payload
- `401 Unauthorized` - Missing or invalid JWT
- `403 Forbidden` - User is not allowed to access that resource
- `404 Not Found` - Requested resource does not exist
- `409 Conflict` - Username already exists

---

## Project Structure

```text
flask-c10-summative-lab-sessions-and-jwt-clients/
├── app.py
├── config.py
├── models.py
├── seed.py
├── requirements.txt
├── README.md
├── .gitignore
├── resources/
│   ├── __init__.py
│   ├── auth.py
│   └── notes.py
├── tests/
│   ├── __init__.py
│   └── test_api.py
└── migrations/
    └── versions/
```

---

## Technologies Used

- Python 3.12
- Flask
- Flask-RESTful
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-Bcrypt
- Flask-JWT-Extended
- SQLite
- pytest

---

## Running Tests

To run the automated tests:

```bash
pytest
```

This project includes tests covering:

- Authentication
- Note CRUD operations
- Authorization checks
- Pagination
- Error handling

---

## Notes

- The seeded users are for demo purposes only
- The default seeded password is `password123`
- The app is designed for local development and learning purposes
