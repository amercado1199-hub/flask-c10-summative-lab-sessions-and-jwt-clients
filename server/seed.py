from config import app, db
from models import User, Note

with app.app_context():
    print("Clearing database...")
    User.query.delete()
    Note.query.delete()

    print("Creating users...")

    user1 = User(username="alyssa")
    user1.password_hash = "password123"

    user2 = User(username="testuser")
    user2.password_hash = "password123"

    db.session.add_all([user1, user2])
    db.session.commit()

    print("Creating notes...")

    notes = [
        Note(title="Homework", content="Finish Flask backend lab.", user_id=user1.id),
        Note(title="Groceries", content="Buy milk, eggs, and bread.", user_id=user1.id),
        Note(title="Workout", content="Do 30 minutes of cardio.", user_id=user2.id),
    ]

    db.session.add_all(notes)
    db.session.commit()

    print("Done seeding!")