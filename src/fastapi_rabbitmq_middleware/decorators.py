consumer_registry = {}


def register_consumer(queue_name: str, func):
    """
    Register a consumer to a queue

    Args:
        queue_name (str): Name of the queue
        func (Callable): Function to be registered as a consumer
    """

    if queue_name not in consumer_registry:
        consumer_registry[queue_name] = func


def get_consumer_func(queue_name):
    """
    Get the consumer function for a queue

    Args:
        queue_name (str): Name of the queue

    Returns:
        Callable: Consumer function
    """

    return consumer_registry.get(queue_name, None)


def rabbitmq_consumer(queue_name):
    """
    Decorator to register a function as a consumer to a queue

    Args:
        queue_name (str): Name of the queue
    """

    def wrapper(func):
        register_consumer(queue_name, func)
        return func

    return wrapper


def get_registered_queues():
    """
    Get the list of registered queues

    Returns:
        List[str]: List of registered queues
    """

    return list(consumer_registry.keys())
