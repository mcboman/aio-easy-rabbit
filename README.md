# aio-easy-rabbit

An opinionated way to use RabbitMQ in Asyncio based frameworks.


# Installation

to be continued ...


# Usage example

Simple consumer example in a FastAPI

```python

from fastapi import FastAPI
from aio_easy_rabbit.connection import (
    connect_to_rabbitmq,
    start_listening_to_queue,
)


app = FastAPI()

@rabbitmq_consumer("test_queue")
async def test_consumer(message):
    print(message)


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

```

Key component is the `ConsumerRegistry` that will manage state of all registered queues and their consuming functions.

Note: Each decorated consumer will receive a raw string that needs to be serialized as pleased.


Simple publisher example in FastAPI

```python
from fastapi import FastAPI

from aio_easy_rabbit.connection import (
    connect_to_rabbitmq
)
from aio_easy_rabbit.producers import RabbitMQPublisher

app = FastAPI()


class Message(BaseModel):
    message: str


@app.post("/test/{queue_name}/")
async def test_endpoint(queue_name: str, message: Message):
    await app.state.rabbitmq_publisher.publish_message(queue_name, message)
    return {"message": "Message published"}


@app.on_event("startup")
async def startup_event():
    rabbitmq_connection_string = "amqp://guest:guest@localhost"
    app.state.rabbitmq_connection = await connect_to_rabbitmq(
        rabbitmq_connection_string
    )
    app.state.rabbitmq_publisher = RabbitMQPublisher(rabbitmq_connection_string)

```

