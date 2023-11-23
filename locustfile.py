from locust import HttpUser, task

class SimpleUser(HttpUser):
    @task
    def load_page(self):
        self.client.get("/")