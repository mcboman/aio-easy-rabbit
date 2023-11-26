import asyncio
from fastapi import FastAPI
from aio_easy_rabbit.connection import (
    connect_to_rabbitmq,
    start_listening_to_queue,
)
from aio_easy_rabbit.decorators import rabbitmq_consumer
from aio_easy_rabbit.consumer_registry import ConsumerRegistry
from aio_easy_rabbit.producers import RabbitMQPublisher
from pydantic import BaseModel

app = FastAPI()


class Message(BaseModel):
    message: str


@rabbitmq_consumer("test_queue")
async def test_consumer(message):
    print(message)


@app.post("/test/{queue_name}/")
async def test_endpoint(queue_name: str, message: Message):
    await app.state.rabbitmq_publisher.publish_message(queue_name, message)
    return {"message": "Message published"}


@app.on_event("startup")
async def startup_event():
    registry = ConsumerRegistry()
    rabbitmq_connection_string = "amqp://guest:guest@localhost"
    app.state.rabbitmq_connection = await connect_to_rabbitmq(
        rabbitmq_connection_string
    )
    for queue_name in registry.get_registered_queues():
        asyncio.create_task(
            start_listening_to_queue(app.state.rabbitmq_connection, queue_name)
        )

    app.state.rabbitmq_publisher = RabbitMQPublisher(rabbitmq_connection_string)


@app.on_event("shutdown")
async def shutdown_event():
    await app.state.rabbitmq_connection.close_all_connections()
    await app.state.rabbitmq_connection.close()
