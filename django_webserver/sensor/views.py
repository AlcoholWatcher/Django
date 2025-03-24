#views.py
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
import json
from .models import SensorData  # SensorData 모델 임포트
from django.shortcuts import redirect
from django.utils import timezone
# CSRF 토큰을 반환하는 뷰
@csrf_exempt
def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrf_token': csrf_token})

# CSRF 보호 해제 → ESP32에서 POST 요청 가능
from django.shortcuts import redirect

@csrf_exempt
def receive_sensor_data(request):
    if request.method == 'POST':
        if not request.body:
            return JsonResponse({'status': 'failure', 'message': 'Empty request body'}, status=400)

        try:
            data = json.loads(request.body)
            sensor_value = data.get('sensor_value')
            device = data.get('device')
            timestamp = data.get('timestamp')

            if device is None:
                return JsonResponse({'status': 'failure', 'message': 'No device provided'}, status=400)

            if sensor_value is None:
                sensor_value = 0  # 기본값 설정

            if timestamp is None:
                timestamp = timezone.now()  # 현재 시간으로 설정

            # 이전 최신 데이터의 is_latest를 False로 업데이트
            SensorData.objects.filter(device=device, is_latest=True).update(is_latest=False)

            # 새로운 데이터 저장
            SensorData.objects.create(device=device, sensor_value=sensor_value, timestamp=timestamp, is_latest=True)

            # JSON 응답 반환
            return JsonResponse({'status': 'success', 'message': 'Data received successfully', 'device': device, 'sensor_value': sensor_value, 'timestamp': str(timestamp)})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'failure', 'message': 'Invalid JSON'}, status=400)
    elif request.method == 'GET':
        return JsonResponse({'status': 'success', 'message': 'GET request to /sensor/post/'})
    return JsonResponse({'status': 'failure', 'message': 'Method not allowed'}, status=405)# 홈 페이지 뷰
def home(request):
    return HttpResponse("Hello from the main page!")

def display_latest_data(request):
    latest_data = SensorData.objects.filter(is_latest=True).order_by('-id')  # 최신 데이터 가져오기
    return render(request, 'sensor/latest_data.html', {'latest_data': latest_data})