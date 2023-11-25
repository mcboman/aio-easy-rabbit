from .consumer_registry import ConsumerRegistry


def rabbitmq_consumer(queue_name):
    """
    Decorator to register a function as a consumer to a queue

    Args:
        queue_name (str): Name of the queue
    """

    def wrapper(func):
        registry = ConsumerRegistry()
        registry.register_consumer(queue_name, func)
        return func

    return wrapper
