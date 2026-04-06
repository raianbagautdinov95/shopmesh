from datetime import datetime
from uuid import uuid4

from app.events.publisher import publisher
from app.models.notification import Notification, NotificationStatus
from app.repositories.notification import NotificationRepository
from app.schemas.notification import (
    NotificationCreateRequest,
    NotificationListResponse,
    NotificationResponse,
    NotificationStatusUpdateRequest,
)


class NotificationService:
    def __init__(self, repository: NotificationRepository) -> None:
        self.repository = repository

    def list_notifications(
        self,
        actor_email: str,
        actor_role: str,
        *,
        recipient: str | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> NotificationListResponse:
        effective_user = None if actor_role == "admin" else actor_email
        items = self.repository.list_notifications(
            user_email=effective_user, recipient=recipient, status=status, limit=limit, offset=offset
        )
        payload = [self._to_response(item) for item in items]
        return NotificationListResponse(items=payload, count=len(payload), limit=limit, offset=offset)

    def create_notification(self, actor_email: str, payload: NotificationCreateRequest) -> NotificationResponse:
        notification = Notification(
            user_email=actor_email,
            recipient=payload.recipient,
            channel=payload.channel,
            template_key=payload.template_key,
            subject=payload.subject,
            message=payload.message,
            related_order_id=payload.related_order_id,
            related_payment_id=payload.related_payment_id,
            status=NotificationStatus.queued.value,
        )
        created = self.repository.create(notification)

        # mock send provider
        created.provider_message_id = f"msg_{uuid4().hex[:16]}"
        created.status = NotificationStatus.sent.value
        created.sent_at = datetime.utcnow()
        created = self.repository.update(created)

        publisher.publish(
            "notification.sent",
            {
                "notification_id": created.id,
                "recipient": created.recipient,
                "channel": created.channel,
                "status": created.status,
            },
        )
        return self._to_response(created)

    def get_notification(self, actor_email: str, actor_role: str, notification_id: int) -> NotificationResponse:
        notification = self.repository.get_by_id(notification_id)
        if not notification:
            raise ValueError("Notification not found")
        if actor_role != "admin" and notification.user_email != actor_email:
            raise PermissionError("Not enough permissions")
        return self._to_response(notification)

    def update_status(
        self,
        actor_role: str,
        notification_id: int,
        payload: NotificationStatusUpdateRequest,
    ) -> NotificationResponse:
        if actor_role != "admin":
            raise PermissionError("Not enough permissions")

        notification = self.repository.get_by_id(notification_id)
        if not notification:
            raise ValueError("Notification not found")

        notification.status = payload.status
        notification.failure_reason = payload.failure_reason
        if payload.status == NotificationStatus.sent.value and notification.sent_at is None:
            notification.sent_at = datetime.utcnow()
        notification = self.repository.update(notification)

        publisher.publish(
            "notification.status_updated",
            {"notification_id": notification.id, "status": notification.status},
        )
        return self._to_response(notification)

    def mark_read(self, actor_email: str, actor_role: str, notification_id: int) -> NotificationResponse:
        notification = self.repository.get_by_id(notification_id)
        if not notification:
            raise ValueError("Notification not found")
        if actor_role != "admin" and notification.user_email != actor_email:
            raise PermissionError("Not enough permissions")
        notification.is_read = True
        notification = self.repository.update(notification)
        return self._to_response(notification)

    @staticmethod
    def _to_response(notification: Notification) -> NotificationResponse:
        return NotificationResponse(
            id=notification.id,
            user_email=notification.user_email,
            recipient=notification.recipient,
            channel=notification.channel,
            template_key=notification.template_key,
            subject=notification.subject,
            message=notification.message,
            related_order_id=notification.related_order_id,
            related_payment_id=notification.related_payment_id,
            status=notification.status,
            provider_message_id=notification.provider_message_id,
            failure_reason=notification.failure_reason,
            is_read=notification.is_read,
            created_at=notification.created_at,
            sent_at=notification.sent_at,
        )
