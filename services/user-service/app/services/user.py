from sqlalchemy.orm import Session

from app.models.user import UserProfile
from app.repositories.user import UserRepository
from app.schemas.user import UserProfileUpdateRequest


class UserService:
    def __init__(self, db: Session) -> None:
        self.repository = UserRepository(db)

    def list_users(self) -> list[UserProfile]:
        return self.repository.list_users()

    def get_user_by_id(self, user_id: int) -> UserProfile | None:
        return self.repository.get_by_id(user_id)

    def get_or_create_current_user(self, *, email: str, role: str) -> UserProfile:
        return self.repository.get_or_create_from_identity(email=email, role=role)

    def update_current_user(
        self,
        profile: UserProfile,
        payload: UserProfileUpdateRequest,
    ) -> UserProfile:
        return self.repository.update_profile(
            profile,
            full_name=payload.full_name,
            phone=payload.phone,
            city=payload.city,
            bio=payload.bio,
        )

    def update_role(self, profile: UserProfile, role: str) -> UserProfile:
        return self.repository.update_role(profile, role)

    def set_active(self, profile: UserProfile, is_active: bool) -> UserProfile:
        return self.repository.set_active(profile, is_active)
