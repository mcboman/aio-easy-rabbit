import aio_pika
from .consumer_registry import ConsumerRegistry


async def connect_to_rabbitmq(rabbitmq_connection_string: str):
    connection = await aio_pika.connect_robust(rabbitmq_connection_string)
    return connection


async def start_listening_to_queue(connection, queue_name):
    """
    Start listening to a queue

    Args:
        connection (aio_pika.Connection): RabbitMQ connection
        queue_name (str): Name of the queue
    """
    async with connection:
        registry = ConsumerRegistry()
        channel = await connection.channel()
        queue = await channel.declare_queue(queue_name, durable=True)

        async for message in queue:
            await process_message(message, registry, queue_name)


async def process_message(
    message: aio_pika.IncomingMessage, registry: ConsumerRegistry, queue_name: str
):
    """
    Process and manually acknowledge the message.

    Params:
        message (IncomingMessage): The message from the queue.
        registry (ConsumerRegistry): The registry with consumer functions.
        queue_name (str): The name of the queue.
    """
    try:
        consumer_func = registry.get_consumer_func(queue_name)
        if consumer_func:
            await consumer_func(message.body)
        await message.ack()
    except Exception as e:
        await message.nack(requeue=True)
        raise e
