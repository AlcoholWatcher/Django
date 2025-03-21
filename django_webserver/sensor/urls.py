from django.urls import path
from . import views

urlpatterns = [
    path('receive/', views.receive_sensor_data, name='receive_sensor_data'),
    path('', views.home, name='sensor_index'),  # 홈 페이지는 나중에
    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),
]
