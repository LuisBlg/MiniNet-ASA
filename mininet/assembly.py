"""Racine de composition : seul module qui connaît les composants concrets."""
from contextlib import contextmanager
from dataclasses import dataclass
from importlib import import_module
from .architecture import COMPONENTS, CALLS, EVENT
from .connectors import ProcedureCall, MessageBus, PublisherPort

@dataclass
class Application:
    components: dict
    connectors: dict

    @property
    def console(self):
        return self.components['ConsoleUI']

@contextmanager
def assemble(path, **console_io):
    components, connectors = {}, {}
    bus_name,publisher,publish_port,subscriber,subscribe_port = EVENT
    bus = connectors[bus_name] = MessageBus()
    try:
        for name, module_class in COMPONENTS.items():
            module, cls = module_class.split('.')
            factory = getattr(import_module(f'.components.{module}',__package__),cls)
            kwargs = {}
            for call in CALLS:
                if call.consumer == name:
                    connector = ProcedureCall(call.name,components[call.provider],call.operations)
                    connectors[call.name] = kwargs[call.required] = connector
            if name == publisher:
                kwargs[publish_port] = PublisherPort(bus)
            if name == 'Storage':
                kwargs['path'] = path
            if name == 'ConsoleUI':
                kwargs.update(console_io)
            instance = components[name] = factory(**kwargs)
            if name == subscriber:
                bus.subscribe(getattr(instance,subscribe_port))
        yield Application(components,connectors)
    finally:
        if 'Storage' in components:
            components['Storage'].close()
