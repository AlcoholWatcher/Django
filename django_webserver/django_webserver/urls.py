# django_webserver/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('sensor.urls')),  # 홈 페이지 경로는 ''로 설정
]
