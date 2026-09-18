import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from django.utils import timezone as django_timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import InterruptionEventSerializer, LatestInterruptionSerializer
from .services import (
    InterruptionServiceError,
    LatestInterruptionNotFound,
    get_all_interruptions,
    get_latest_interruption,
)


logger = logging.getLogger(__name__)
VECO_TIME_ZONE = 'Asia/Manila'


def _resolve_date_filter(raw_date):
    if raw_date is None:
        return None
    if raw_date.casefold() == 'today':
        return django_timezone.localdate(timezone=ZoneInfo(VECO_TIME_ZONE))
    try:
        return datetime.strptime(raw_date, '%Y-%m-%d').date()
    except ValueError as exc:
        raise ValueError('date must be YYYY-MM-DD or today.') from exc


class InterruptionListView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        raw_date = request.query_params.get('date')
        try:
            target_date = _resolve_date_filter(raw_date)
        except ValueError as exc:
            return Response(
                {
                    'success': False,
                    'message': str(exc),
                    'data': None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            interruptions = get_all_interruptions(target_date=target_date)
        except InterruptionServiceError:
            logger.exception('Unable to build the VECO interruption collection.')
            return Response(
                {
                    'success': False,
                    'message': 'Unable to retrieve the VECO interruption calendar.',
                    'data': None,
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        serializer = InterruptionEventSerializer(instance=interruptions, many=True)
        return Response(
            {
                'success': True,
                'message': 'VECO interruption calendar retrieved.',
                'data': serializer.data,
                'meta': {
                    'count': len(serializer.data),
                    'date': target_date.isoformat() if target_date else None,
                    'timezone': VECO_TIME_ZONE,
                    'source': 'VECO Interruption Calendar',
                },
            }
        )


class LatestInterruptionView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            interruption = get_latest_interruption()
        except LatestInterruptionNotFound:
            return Response(
                {
                    'success': False,
                    'message': 'No VECO service interruption was found.',
                    'data': None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except InterruptionServiceError:
            logger.exception('Unable to build the latest VECO interruption schedule.')
            return Response(
                {
                    'success': False,
                    'message': 'Unable to retrieve the complete VECO interruption schedule.',
                    'data': None,
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        serializer = LatestInterruptionSerializer(instance=interruption)
        return Response(
            {
                'success': True,
                'message': 'Latest VECO service interruption retrieved.',
                'data': serializer.data,
            }
        )
