import json
from random import randint
from uuid import uuid4
from locust import HttpUser, between, task


class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def index(self):
        generated_input = [uuid4().hex for _ in range(randint(0, 50))]
        with self.client.post("/", json=generated_input, catch_response=True) as response:
            print(response.json())
            if response.json() is None:
                response.failure("Not json!")
        