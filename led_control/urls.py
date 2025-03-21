from django.urls import path
from .views import control_led, home

urlpatterns = [
    path('led/', control_led, name='control_led'),
    path('', home, name='home'),  # 홈 페이지 URL 추가
]