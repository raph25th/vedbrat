from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models import User


def seed() -> None:
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.email == "admin@example.com").first():
            db.add(
                User(
                    name="Admin",
                    email="admin@example.com",
                    role="admin",
                    is_allowed_to_connect_bot=True,
                    password_hash=get_password_hash("admin123"),
                )
            )
            db.commit()
            print("Created admin@example.com / admin123")
        else:
            print("Admin user already exists")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
