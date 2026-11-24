from ..domain import DomainError, username

class FriendManager:
    def __init__(self, store):
        self.store = store

    def _other(self, uid, name):
        other = self.store.user_id(username(name))
        if uid == other:
            raise DomainError('Impossible de s’ajouter soi-même.')
        return other

    def add(self, uid, name):
        self.store.add_friend(uid, self._other(uid,name))

    def remove(self, uid, name):
        self.store.remove_friend(uid, self._other(uid,name))

    def list(self, uid):
        return self.store.list_friends(uid)
