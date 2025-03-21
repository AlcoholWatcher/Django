from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
import json
from .models import SensorData  # SensorData 모델 임포트

# CSRF 토큰을 반환하는 뷰
@csrf_exempt
def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrf_token': csrf_token})

# CSRF 보호 해제 → ESP32에서 POST 요청 가능
@csrf_exempt
def receive_sensor_data(request):
    if request.method == 'POST':
        if not request.body:
            return JsonResponse({'status': 'failure', 'message': 'Empty request body'}, status=400)

        try:
            data = json.loads(request.body)
            sensor_value = data.get('sensor_value')
            device = data.get('device')

            if sensor_value is None or device is None:
                return JsonResponse({'status': 'failure', 'message': 'No sensor_value or device provided'}, status=400)

            # 이전 최신 데이터의 is_latest를 False로 업데이트
            SensorData.objects.filter(device=device, is_latest=True).update(is_latest=False)

            # 새로운 데이터 저장
            SensorData.objects.create(device=device, sensor_value=sensor_value, is_latest=True)

            return JsonResponse({'status': 'success', 'sensor_value': sensor_value})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'failure', 'message': 'Invalid JSON'}, status=400)

    return JsonResponse({'status': 'failure', 'message': 'Method not allowed'}, status=405)
# 홈 페이지 뷰
def home(request):
    return HttpResponse("Hello from the main page!")

# 데이터 리스트를 표시하는 뷰
def data_list(request):
    sensor_data = SensorData.objects.filter(is_latest=True)  # 최신 데이터만 가져옵니다.
    return render(request, 'sensor/data_list.html', {'sensor_data': sensor_data})
