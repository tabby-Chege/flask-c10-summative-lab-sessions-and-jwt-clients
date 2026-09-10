from server.app import create_app
from server.extensions import db
from server.models import Note, User


def get_or_create_user(username, password):
    user = User.query.filter_by(username=username).first()

    if not user:
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

    return user


def seed():
    app = create_app()

    with app.app_context():
        tabby = get_or_create_user("Tabby", "password123")
        prince = get_or_create_user("Prince", "password123")

        notes = [
            {
                "title": "Morning Routine",
                "content": "Plan the day and review priorities.",
                "category": "personal",
            },
            {
                "title": "Flask Backend Setup",
                "content": "Build models, CRUD routes, and authentication.",
                "category": "work",
            },
            {
                "title": "Grocery List",
                "content": "Milk, eggs, coffee beans, and bread.",
                "category": "personal",
            },
            {
                "title": "Project Architecture",
                "content": "Use Blueprints, SQLAlchemy, JWT, and Marshmallow.",
                "category": "work",
            },
            {
                "title": "Study Notes",
                "content": "Review Flask-Migrate and database relationships.",
                "category": "school",
            },
            {
                "title": "Reading List",
                "content": "Read documentation about secure JWT authentication.",
                "category": "school",
            },
            {
                "title": "Sprint Checklist",
                "content": "Test protected routes and prepare the final submission.",
                "category": "work",
            },
        ]

        for note_data in notes:
            existing_note = Note.query.filter_by(
                user_id=tabby.id,
                title=note_data["title"],
            ).first()

            if not existing_note:
                db.session.add(
                    Note(
                        title=note_data["title"],
                        content=note_data["content"],
                        category=note_data["category"],
                        user_id=tabby.id,
                    )
                )

        prince_note = Note.query.filter_by(
            user_id=prince.id,
            title="Prince Private Note",
        ).first()

        if not prince_note:
            db.session.add(
                Note(
                    title="Prince Private Note",
                    content="This note belongs only to Prince.",
                    category="private",
                    user_id=prince.id,
                )
            )

        db.session.commit()

        print("Database seeded successfully.")
        print("Users: Tabby, Prince")
        print("Tabby notes: 7")
        print("Prince notes: 1")


if __name__ == "__main__":
    seed()
