from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sensor/', include('sensor.urls')),  # sensor.urls를 포함
]
