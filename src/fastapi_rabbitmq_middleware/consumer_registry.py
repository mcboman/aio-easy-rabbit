class ConsumerRegistry:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConsumerRegistry, cls).__new__(cls, *args, **kwargs)
            cls._instance._registry = {}
        return cls._instance

    def register_consumer(self, queue_name: str, func):
        self._instance._registry[queue_name] = func

    def get_consumer_func(self, queue_name: str):
        return self._instance._registry.get(queue_name)

    def get_registered_queues(self):
        return list(self._instance._registry.keys())
