#sensor\urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='sensor_home'),  # 홈 페이지
    path('sensor-data/', views.receive_sensor_data, name='receive_sensor_data'),  # POST 요청을 받는 경로
    path('latest/', views.display_latest_data, name='display_latest_data'),
    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),  # CSRF 토큰
    path('get-latest-data/', views.get_latest_sensor_data, name='get_latest_sensor_data'), # 센서 데이터 요청을 처리하는 경로
]
