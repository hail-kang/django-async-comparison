from django.urls import path
from . import views

urlpatterns = [
    path('sync-io/', views.sync_io_view, name='sync-io'),
    path('async-io/', views.async_io_view, name='async-io'),
    path('sync-cpu/', views.sync_cpu_view, name='sync-cpu'),
    path('async-cpu/', views.async_cpu_view, name='async-cpu'),
    path('sync-json/', views.sync_large_json_view, name='sync-json'),
    path('async-json/', views.async_large_json_view, name='async-json'),
]
