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
            # 요청 본문을 JSON으로 파싱
            data = json.loads(request.body)
            sensor_value = data.get('sensor_value')
            device = data.get('device')

            # 필수 데이터 확인
            if sensor_value is None or device is None:
                return JsonResponse({'status': 'failure', 'message': 'No sensor_value or device provided'}, status=400)

            # 데이터베이스에 저장
            SensorData.objects.create(device=device, sensor_value=sensor_value)

            # 성공 응답
            return JsonResponse({'status': 'success', 'sensor_value': sensor_value})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'failure', 'message': 'Invalid JSON'}, status=400)

    return JsonResponse({'status': 'failure', 'message': 'Method not allowed'}, status=405)

# 홈 페이지 뷰
def home(request):
    return HttpResponse("Hello from the main page!")

# 데이터 리스트를 표시하는 뷰
def data_list(request):
    sensor_data = SensorData.objects.all()  # 모든 센서 데이터 가져오기
    return render(request, 'sensor/data_list.html', {'sensor_data': sensor_data})
