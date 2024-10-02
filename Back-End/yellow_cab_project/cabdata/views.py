import logging
from django.http import JsonResponse
from django.views import View
from .models import YellowCab
from .import_yellow_cab_data import manage_data
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import datetime

# Get an instance of a logger
logger = logging.getLogger(__name__)

class TripCountView(View):
    def get(self, request):
        date_str = request.GET.get('date')
        if not date_str:
            return JsonResponse({'error': 'Missing date parameter'}, status=400)
        try:
            date = timezone.make_aware(datetime.strptime(date_str, '%Y-%m-%d'))
        except ValueError:
            return JsonResponse({'error': 'Invalid date format. Expected format: YYYY-MM-DD'}, status=400)

        manage_data(date.year, date.month)

        start_datetime = timezone.make_aware(datetime.combine(date, datetime.min.time()))
        end_datetime = timezone.make_aware(datetime.combine(date, datetime.max.time()))

        trip_counts = YellowCab.objects.filter(
            tpep_pickup_datetime__range=(start_datetime, end_datetime)
        ).extra(select={'hour': 'HOUR(tpep_pickup_datetime)'}).values('hour').annotate(count=Count('id'))

        response_data = list(trip_counts)
        logger.debug("Trip counts data sent to frontend: %s", response_data)

        return JsonResponse(response_data, safe=False)


class CheapestHourView(View):
    def get(self, request):
        start_location = request.GET.get('start_location')
        end_location = request.GET.get('end_location')
        date_str = request.GET.get('date')

        if not date_str:
            return JsonResponse({'error': 'Missing date parameter'}, status=400)
        if not start_location or not end_location:
            return JsonResponse({'error': 'Missing location parameters'}, status=400)

        try:
            date = timezone.make_aware(datetime.strptime(date_str, '%Y-%m-%d'))
        except ValueError:
            return JsonResponse({'error': 'Invalid date format. Expected format: YYYY-MM-DD'}, status=400)

        manage_data(date.year, date.month)

        start_datetime = timezone.make_aware(datetime.combine(date, datetime.min.time()))
        end_datetime = timezone.make_aware(datetime.combine(date, datetime.max.time()))

        trips = YellowCab.objects.filter(
            tpep_pickup_datetime__range=(start_datetime, end_datetime),
            PULocationID=start_location,
            DOLocationID=end_location
        ).extra(select={'hour': 'HOUR(tpep_pickup_datetime)'}).values('hour').annotate(avg_fare=Avg('total_amount'))

        if not trips:
            return JsonResponse({'error': 'No trips found for the given criteria'}, status=404)

        cheapest_hour = min(trips, key=lambda x: x['avg_fare'])
        logger.debug("Cheapest hour data sent to frontend: %s", cheapest_hour)

        return JsonResponse(cheapest_hour, safe=False)
