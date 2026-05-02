from locust import HttpUser, task, between, tag

class WebsiteUser(HttpUser):
    """
    User class that defines the behavior of a simulated user.
    The user will randomly pick tasks and execute them based on tags.
    """
    # Time each simulated user will wait between executing tasks,
    # in this case between 0.5 and 2.5 seconds.
    wait_time = between(0.5, 2.5)

    @tag("sync_io")
    @task
    def sync_io_task(self):
        """Task that hits the synchronous I/O-bound endpoint."""
        self.client.get("/test/sync-io/")

    @tag("async_io")
    @task
    def async_io_task(self):
        """Task that hits the asynchronous I/O-bound endpoint."""
        self.client.get("/test/async-io/")

    @tag("sync_cpu")
    @task
    def sync_cpu_task(self):
        """Task that hits the synchronous CPU-bound endpoint."""
        self.client.get("/test/sync-cpu/")

    @tag("async_cpu")
    @task
    def async_cpu_task(self):
        """Task that hits the asynchronous CPU-bound endpoint."""
        self.client.get("/test/async-cpu/")

    @tag("sync_json")
    @task
    def sync_json_task(self):
        """Task that hits the synchronous large JSON endpoint."""
        self.client.get("/test/sync-json/")

    @tag("async_json")
    @task
    def async_json_task(self):
        """Task that hits the asynchronous large JSON endpoint."""
        self.client.get("/test/async-json/")
