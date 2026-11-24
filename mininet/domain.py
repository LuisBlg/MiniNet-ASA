"""Contrats de données partagés, sans dépendance vers un composant."""
from dataclasses import dataclass
from urllib.parse import urlsplit
import re

class DomainError(ValueError):
    """Erreur métier destinée à l'utilisateur."""

@dataclass(frozen=True)
class Post:
    id: int
    author: str
    kind: str
    content: str
    created: str

@dataclass(frozen=True)
class Message:
    id: int
    sender: str
    recipient: str
    body: str
    created: str

@dataclass(frozen=True)
class MessageSent:
    recipient: int
    sender: str
    message_id: int


def text(value: str, label: str, limit: int) -> str:
    value = value.strip()
    if not value or len(value) > limit or any(not c.isprintable() for c in value):
        raise DomainError(f"{label} : 1 à {limit} caractères imprimables attendus.")
    return value


def username(value: str) -> str:
    value = value.strip().lower()
    if not re.fullmatch(r'[a-z0-9_]{3,24}', value):
        raise DomainError('Pseudo : 3 à 24 lettres ASCII, chiffres ou underscores.')
    return value


def link(value: str) -> str:
    value = text(value, 'Lien', 500)
    try:
        parsed = urlsplit(value)
        valid = parsed.scheme in ('http', 'https') and bool(parsed.hostname) and not any(c.isspace() for c in value)
        _ = parsed.port
    except ValueError:
        valid = False
    if not valid:
        raise DomainError('Lien HTTP ou HTTPS valide attendu.')
    return value
