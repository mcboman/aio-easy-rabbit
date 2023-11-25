import aio_pika
from .decorators import get_consumer_func


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
        channel = await connection.channel()
        queue = await channel.declare_queue(queue_name, durable=True)

        async for message in queue:
            consumer_func = get_consumer_func(queue_name)
            if consumer_func:
                await consumer_func(message.body)
