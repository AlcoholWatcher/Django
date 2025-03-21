# sensor/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='sensor_home'),  # 홈 페이지
    path('post/', views.receive_sensor_data, name='receive_sensor_data'),  # POST 요청을 받는 경로
    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),  # CSRF 토큰
]
