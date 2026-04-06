from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email.lower()).first()

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(
        self,
        *,
        email: str,
        full_name: str,
        hashed_password: str,
        role: str = "user",
    ) -> User:
        user = User(
            email=email.lower(),
            full_name=full_name.strip(),
            hashed_password=hashed_password,
            role=role,
            is_active=True,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_password(self, user: User, hashed_password: str) -> User:
        user.hashed_password = hashed_password
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def deactivate(self, user: User) -> User:
        user.is_active = False
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user