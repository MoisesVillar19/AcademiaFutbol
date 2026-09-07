class EventBus:
    def __init__(self):
        self._handlers = {}

    def subscribe(self, event_name: str, handler):
        if event_name not in self._handlers:
            self._handlers[event_name] = []
        self._handlers[event_name].append(handler)

    def publish(self, event_name: str, *args, **kwargs):
        for handler in self._handlers.get(event_name, []):
            handler(*args, **kwargs)


event_bus = EventBus()