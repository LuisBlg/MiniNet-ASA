from ..domain import DomainError, MessageSent, text, username

class MessageService:
    def __init__(self, store, events):
        self.store = store
        self.events = events

    def send(self, uid, recipient, body):
        other = self.store.user_id(username(recipient))
        if uid == other:
            raise DomainError('Impossible de s’envoyer un message.')
        body = text(body,'Message',500)
        sender = self.store.user_name(uid)
        message_id = self.store.create_message(uid,other,body)
        # Après validation et commit ; aucun corps de message sur le bus.
        self.events.publish(MessageSent(other,sender,message_id))
        return message_id

    def history(self, uid):
        return self.store.messages(uid)
