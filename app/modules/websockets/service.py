from app.modules.websockets.connection_manager import manager


async def push_notification(notification):

    await manager.send_notification(
        user_id=str(notification.recipient_user_id),
        payload={
            "id": str(notification.id),
            "type": notification.notification_type,
            "title": notification.title,
            "message": notification.message,
            "ticket_id": (
                str(notification.ticket_id)
                if notification.ticket_id
                else None
            ),
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat(),
        },
    )