import asyncio
import logging
import random
from asyncio.log import logger
from datetime import datetime
from typing import List, Tuple
from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import dispatcher


class Response(BaseModel):
    start: datetime
    value: float
    data: str
    



logger = logging.getLogger(__name__)

shared_semaphore = dispatcher.NonBlockSema(1)

@dispatcher.CorkDispatcher(max_latency_in_ms=5000 * 1000, max_batch_size=50, shared_sema=shared_semaphore)
async def batch_me(data: Tuple[str]) -> datetime:
    data = list(data)
    # logger.info(f"Got inference request: {data}")
    start = datetime.now()
    delay = random.random()
    await asyncio.sleep(0)
    # logger.info(f"start: {start}, value: {delay}, data: {data}")
    responses = [Response(start=start, value=delay, data=d) for d in data]
    # logger.info(f"Got result: {responses}")
    return responses

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()



app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    logging.error(f"{exc_str}")
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.post("/", response_model=List[Response])
async def enpoint(data: List) -> List[Response]:
    tasks = [
        batch_me(i)
        for i in data
    ]
    return await asyncio.gather(*tasks)
