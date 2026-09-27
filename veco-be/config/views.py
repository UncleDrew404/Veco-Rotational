from django.http import JsonResponse


def health(request):
    """Liveness probe used by Railway health checks."""
    return JsonResponse({'status': 'ok'})
