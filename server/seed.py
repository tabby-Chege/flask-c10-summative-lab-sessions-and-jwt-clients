from server.app import create_app
from server.extensions import db
from server.models import User, Note

app = create_app()

with app.app_context():
    print("Ensuring database tables exist...")
    db.create_all()  # <-- Automatically creates tables if they are missing!

    print("Clearing existing data...")
    Note.query.delete()
    User.query.delete()

    print("Creating test users...")
    user1 = User(username="amina")
    user1.set_password("password123")

    user2 = User(username="brian")
    user2.set_password("password123")

    db.session.add_all([user1, user2])
    db.session.commit()

    print("Creating sample notes...")
    notes = [
        # Amina's notes (7 notes to test pagination with per_page=5)
        Note(title="Morning Routine", content="Meditation and quick jog at 6 AM.", user_id=user1.id),
        Note(title="Flask Backend Setup", content="Build models, CRUD routes, and pagination.", user_id=user1.id),
        Note(title="Grocery List", content="Milk, eggs, coffee beans, bread.", user_id=user1.id),
        Note(title="Project Architecture", content="Use Blueprints and Flask-JWT-Extended.", user_id=user1.id),
        Note(title="Workout Log", content="Bench press 3x10, Squats 4x8.", user_id=user1.id),
        Note(title="Reading List", content="Designing Data-Intensive Applications.", user_id=user1.id),
        Note(title="Sprint Checklist", content="Verify protected routes and submit repo.", user_id=user1.id),

        # Brian's notes (To test unauthorized access prevention)
        Note(title="Brian's Private Note", content="Amina should not see or edit this.", user_id=user2.id),
        Note(title="Meeting Prep", content="Discuss schema updates with the group.", user_id=user2.id),
    ]

    db.session.add_all(notes)
    db.session.commit()

    print("Database successfully seeded!")