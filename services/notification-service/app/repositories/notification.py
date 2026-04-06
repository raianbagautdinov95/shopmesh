from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, notification: Notification) -> Notification:
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def get_by_id(self, notification_id: int) -> Notification | None:
        return self.db.get(Notification, notification_id)

    def list_notifications(
        self,
        *,
        user_email: str | None = None,
        recipient: str | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Notification]:
        stmt = select(Notification).order_by(Notification.id.desc()).limit(limit).offset(offset)
        if user_email:
            stmt = stmt.where(Notification.user_email == user_email)
        if recipient:
            stmt = stmt.where(Notification.recipient == recipient)
        if status:
            stmt = stmt.where(Notification.status == status)
        return list(self.db.scalars(stmt).all())

    def update(self, notification: Notification) -> Notification:
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification
