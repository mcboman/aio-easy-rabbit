import asyncio
from fastapi import FastAPI
from src.fastapi_rabbitmq_middleware.connection import (
    connect_to_rabbitmq,
    start_listening_to_queue,
)
from src.fastapi_rabbitmq_middleware.decorators import (
    rabbitmq_consumer,
    get_registered_queues,
)


app = FastAPI()


@rabbitmq_consumer("test_queue")
async def test_consumer(message):
    print(message)


@app.on_event("startup")
async def startup_event():
    app.state.rabbitmq_connection = await connect_to_rabbitmq(
        "amqp://guest:guest@localhost"
    )
    for queue_name in get_registered_queues():
        asyncio.create_task(
            start_listening_to_queue(app.state.rabbitmq_connection, queue_name)
        )
