import time
import asyncio
from asgiref.sync import sync_to_async

def _generate_nested_dict(depth: int = 0, max_depth: int = 5, breadth: int = 5):
    """
    Recursively builds a nested dictionary to simulate a CPU-intensive
    data generation and serialization task.
    """
    if depth >= max_depth:
        return {f"leaf_{i}": i * 3.14 for i in range(breadth)}

    data = {}
    for i in range(breadth):
        # Add some arbitrary calculations to increase CPU load
        key = f"item_{depth}_{i}"
        value = {
            "id": f"{depth}-{i}",
            "calculation": (i + 1) * (depth + 1) ** 2,
            "child": _generate_nested_dict(depth + 1, max_depth, breadth)
        }
        data[key] = value
    return data

class PerformanceRepository:
    """
    This repository simulates data access with different types of latency.
    - I/O-bound operations (e.g., network calls, database access)
    - CPU-bound operations (e.g., complex calculations)
    """

    def get_io_bound_data_sync(self, delay: float):
        """Simulates a synchronous I/O-bound operation."""
        time.sleep(delay)
        return {"message": f"Sync data after {delay}s delay"}

    async def get_io_bound_data_async(self, delay: float):
        """Simulates an asynchronous I/O-bound operation."""
        await asyncio.sleep(delay)
        return {"message": f"Async data after {delay}s delay"}

    def get_cpu_bound_data(self, count: int):
        """Simulates a CPU-bound operation."""
        result = sum(i * i for i in range(count))
        return {"message": f"CPU-bound task result: {result}"}

    def get_complex_json_data_sync(self, max_depth: int, breadth: int):
        """Generates a large, complex, nested dictionary synchronously."""
        return _generate_nested_dict(max_depth=max_depth, breadth=breadth)

    @sync_to_async
    def get_complex_json_data_async(self, max_depth: int, breadth: int):
        """Generates a large, complex, nested dictionary asynchronously."""
        return _generate_nested_dict(max_depth=max_depth, breadth=breadth)


# Single instance of the repository to be used by views
repository = PerformanceRepository()
