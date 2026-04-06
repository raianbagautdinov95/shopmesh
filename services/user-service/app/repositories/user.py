from sqlalchemy.orm import Session

from app.models.user import UserProfile


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_users(self) -> list[UserProfile]:
        return self.db.query(UserProfile).order_by(UserProfile.id.asc()).all()

    def get_by_id(self, user_id: int) -> UserProfile | None:
        return self.db.query(UserProfile).filter(UserProfile.id == user_id).first()

    def get_by_email(self, email: str) -> UserProfile | None:
        return self.db.query(UserProfile).filter(UserProfile.email == email.lower()).first()

    def create(
        self,
        *,
        email: str,
        full_name: str,
        role: str = "user",
        is_active: bool = True,
        phone: str | None = None,
        city: str | None = None,
        bio: str | None = None,
    ) -> UserProfile:
        profile = UserProfile(
            email=email.lower(),
            full_name=full_name.strip(),
            role=role,
            is_active=is_active,
            phone=phone,
            city=city,
            bio=bio,
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def get_or_create_from_identity(self, *, email: str, role: str = "user") -> UserProfile:
        profile = self.get_by_email(email)
        if profile:
            updated = False
            if profile.role != role and role:
                profile.role = role
                updated = True
            if updated:
                self.db.add(profile)
                self.db.commit()
                self.db.refresh(profile)
            return profile

        default_name = email.split("@")[0].replace(".", " ").replace("_", " ").title()
        return self.create(email=email, full_name=default_name, role=role or "user")

    def update_profile(
        self,
        profile: UserProfile,
        *,
        full_name: str | None = None,
        phone: str | None = None,
        city: str | None = None,
        bio: str | None = None,
    ) -> UserProfile:
        if full_name is not None:
            profile.full_name = full_name.strip()
        if phone is not None:
            profile.phone = phone.strip() or None
        if city is not None:
            profile.city = city.strip() or None
        if bio is not None:
            profile.bio = bio.strip() or None

        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def update_role(self, profile: UserProfile, role: str) -> UserProfile:
        profile.role = role
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def set_active(self, profile: UserProfile, is_active: bool) -> UserProfile:
        profile.is_active = is_active
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile
