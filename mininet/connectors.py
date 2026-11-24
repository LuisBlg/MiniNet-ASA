"""Connecteurs de premier rang : appel synchrone et diffusion typée."""
from .domain import MessageSent

class ProcedureCall:
    def __init__(self, name, provider, operations):
        self._name = name
        self._provider = provider
        self._operations = frozenset(operations)
        if not all(callable(getattr(provider, op, None)) for op in self._operations):
            raise TypeError(f'Contrat incomplet : {name}')

    def __getattr__(self, operation):
        if operation not in self._operations:
            raise AttributeError(operation)
        return getattr(self._provider, operation)

class MessageBus:
    """Publish/subscribe synchrone, local, sans file ni rétention."""
    def __init__(self):
        self._subscribers = []

    def subscribe(self, callback):
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def publish(self, event: MessageSent):
        if not isinstance(event, MessageSent):
            raise TypeError('Événement MessageSent attendu')
        for callback in tuple(self._subscribers):
            callback(event)

class PublisherPort:
    """Rôle publisher : expose uniquement la publication."""
    def __init__(self, bus):
        self.bus = bus

    def publish(self, event):
        self.bus.publish(event)
