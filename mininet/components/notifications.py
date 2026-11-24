from collections import defaultdict

class NotificationService:
    """Notifications éphémères, indexées par destinataire."""
    def __init__(self):
        self._pending = defaultdict(list)

    def on_message(self, event):
        self._pending[event.recipient].append(f'Nouveau message de {event.sender} (#{event.message_id}).')

    def take(self, uid):
        return self._pending.pop(uid, [])
