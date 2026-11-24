"""UserManager : compte, authentification et annuaire."""
import hashlib
import hmac
import secrets
from ..domain import DomainError, username

ITERATIONS = 600_000

def _digest(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, ITERATIONS)

class UserManager:
    def __init__(self, store):
        self.store = store

    def register(self, name, password):
        name = username(name)
        if not 8 <= len(password) <= 128 or not password.isprintable():
            raise DomainError('Mot de passe : 8 à 128 caractères imprimables.')
        salt = secrets.token_bytes(16)
        return self.store.create_user(name, salt.hex()+':'+_digest(password,salt).hex())

    def authenticate(self, name, password):
        failure = 'Identifiants incorrects.'
        try:
            name = username(name)
        except DomainError:
            raise DomainError(failure) from None
        if not 8 <= len(password) <= 128:
            raise DomainError(failure)
        row = self.store.credentials(name)
        salt, expected = (row[1].split(':') if row else ('00'*16,'00'*32))
        valid = hmac.compare_digest(_digest(password,bytes.fromhex(salt)).hex(),expected)
        if not row or not valid:
            raise DomainError(failure)
        return row[0]

    def list_users(self, uid):
        return self.store.list_users(uid)

    def name(self, uid):
        return self.store.user_name(uid)
