import aio_pika
import json
import pickle
from asyncio import Semaphore


class RabbitMQPublisher:
    """
    RabbitMQ publisher class
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RabbitMQPublisher, cls).__new__(cls)
            cls._instance._init(*args, **kwargs)
        return cls._instance

    def _init(self, connection_url, max_connections=10):
        """
        params:
            connection_url: RabbitMQ connection URL
            max_connections: Max number of connections to be created
        """
        self.connection_url = connection_url
        self.max_connections = max_connections
        self.connections = []
        self.pool_semaphore = Semaphore(max_connections)

    async def get_connection(self):
        """
        Get a connection from the pool
        """
        await self.pool_semaphore.acquire()
        if self.connections:
            return self.connections.pop()
        else:
            return await aio_pika.connect_robust(self.connection_url)

    async def release_connection(self, connection):
        """
        Release a connection back to the pool
        """
        if len(self.connections) < self.max_connections:
            self.connections.append(connection)
        else:
            await connection.close()
        self.pool_semaphore.release()

    async def publish_message(
        self, queue_name, message_body, serialize_type="pydantic"
    ):
        """
        Publish a message to a queue
        params:
            queue_name: Name of the queue to publish to
            message_body: Message body to be published
            serialize_type: Type of serialization to be used (pydantic, json, pickle)
        """
        connection = await self.get_connection()
        try:
            async with connection.channel() as channel:
                _ = await channel.declare_queue(queue_name, durable=True)
                await channel.default_exchange.publish(
                    aio_pika.Message(
                        body=self.__serialize_message(
                            message_body, serialize_type
                        ).encode()
                    ),
                    routing_key=queue_name,
                )
        finally:
            await self.release_connection(connection)

    def __serialize_message(self, message_body, serialize_type: str):
        match serialize_type.lower().strip():
            case "pydantic":
                return message_body.model_dump_json()
            case "json":
                return json.dumps(message_body)
            case "pickle":
                return pickle.dumps(message_body)
            case _:
                raise NotImplementedError(
                    f"Serialization type {serialize_type} not implemented"
                )

    async def close_all_connections(self):
        """
        Close all connections in the pool
        """
        while self.connections:
            connection = self.connections.pop()
            await connection.close()
