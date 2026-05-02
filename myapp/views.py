from django.http import JsonResponse
from .repository import repository
from asgiref.sync import sync_to_async

# I/O-bound views
def sync_io_view(request):
    """A synchronous view that simulates an I/O-bound operation."""
    data = repository.get_io_bound_data_sync(delay=0.1)
    return JsonResponse(data)

async def async_io_view(request):
    """An asynchronous view that simulates an I/O-bound operation."""
    data = await repository.get_io_bound_data_async(delay=0.1)
    return JsonResponse(data)


# CPU-bound views
def sync_cpu_view(request):
    """A synchronous view that simulates a CPU-bound operation."""
    data = repository.get_cpu_bound_data(count=10_000_000)
    return JsonResponse(data)

# To run a synchronous CPU-bound function in an async view without blocking the
# event loop, we use sync_to_async.
@sync_to_async
def get_cpu_bound_data_async_wrapper(count):
    return repository.get_cpu_bound_data(count)

async def async_cpu_view(request):
    """An asynchronous view that simulates a CPU-bound operation."""
    data = await get_cpu_bound_data_async_wrapper(count=10_000_000)
    return JsonResponse(data)


# Large JSON views (now with complex, nested structure)
def sync_large_json_view(request):
    """A synchronous view that returns a large, complex JSON payload."""
    # A depth of 4 and breadth of 6 creates a very large object
    data = repository.get_complex_json_data_sync(max_depth=4, breadth=6)
    return JsonResponse(data)

async def async_large_json_view(request):
    """An asynchronous view that returns a large, complex JSON payload."""
    data = await repository.get_complex_json_data_async(max_depth=4, breadth=6)
    return JsonResponse(data)
