from django.urls import path

from .views import InterruptionListView, LatestInterruptionView


app_name = 'interruptions'

urlpatterns = [
    path('', InterruptionListView.as_view(), name='list'),
    path('latest/', LatestInterruptionView.as_view(), name='latest'),
]
