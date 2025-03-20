from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # 기본 경로 설정
    path('receive/', views.receive_sensor_data, name='receive_sensor_data'),  # sensor 데이터를 받는 경로
    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),  # CSRF 토큰을 발급받는 URL 추가
]
