import asyncio
import logging
import random
from datetime import datetime
from typing import List, Tuple

from fastapi import FastAPI
from pydantic import BaseModel

import dispatcher


class Response(BaseModel):
    start: datetime
    value: float
    data: str


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


@dispatcher.CorkDispatcher(max_latency_in_ms=5000 * 1000, max_batch_size=50)
async def batch_computation(data: Tuple[str]) -> datetime:
    # simulate log running batch computation (e.g. ML model inference)
    data = list(data)
    start = datetime.now()
    delay = random.random()
    await asyncio.sleep(0.5)
    responses = [Response(start=start, value=delay, data=d) for d in data]
    return responses

app = FastAPI()


@app.post("/", response_model=List[Response])
async def batchable_endpoint(data: List) -> List[Response]:
    # need to pass single item at a time,
    # batching is done by the dispatcher
    tasks = [batch_computation(i) for i in data]
    return await asyncio.gather(*tasks)
