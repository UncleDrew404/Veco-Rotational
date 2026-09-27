from django.contrib import admin
from django.urls import include, path

from config.views import health

urlpatterns = [
    path('health/', health, name='health'),
    path('admin/', admin.site.urls),
    path('api/v1/interruptions/', include('apps.interruptions.urls')),
]
