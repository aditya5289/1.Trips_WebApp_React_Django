from django.urls import path
from .views import TripCountView, CheapestHourView

urlpatterns = [
    path('trip-count/', TripCountView.as_view(), name='trip-count'),
    path('cheapest-hour/', CheapestHourView.as_view(), name='cheapest-hour'),
]
