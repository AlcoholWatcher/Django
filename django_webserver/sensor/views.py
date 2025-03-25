#views.py
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import SensorData  # SensorData 모델 임포트
from django.utils import timezone
from datetime import timedelta
import pytz
# CSRF 토큰을 반환하는 뷰
@csrf_exempt
def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrf_token': csrf_token})

# POST 요청을 처리하는 뷰
@csrf_exempt
def receive_sensor_data(request):
    if request.method == 'POST':
        if not request.body:
            return JsonResponse({'status': 'failure', 'message': 'Empty request body'}, status=400)

        try:
            data = json.loads(request.body)
            alcohol = data.get('alcohol')
            gyro = data.get('gyro')
            motor_speed = data.get('motor_speed')
            device = data.get('device')

            if device is None:
                return JsonResponse({'status': 'failure', 'message': 'No device provided'}, status=400)

            # 이전 최신 데이터의 is_latest를 False로 업데이트
            SensorData.objects.filter(device=device, is_latest=True).update(is_latest=False)

            # 새로운 데이터 저장
            SensorData.objects.create(device=device, alcohol=alcohol, gyro=gyro, motor_speed=motor_speed, is_latest=True)

            # JSON 응답 반환
            return JsonResponse({'status': 'success', 'message': 'Data received successfully', 'device': device})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'failure', 'message': 'Invalid JSON'}, status=400)

    return JsonResponse({'status': 'failure', 'message': 'Method not allowed'}, status=405)


#AJAX
@csrf_exempt
def get_latest_sensor_data(request):
    if request.method == 'GET':
        latest_data = SensorData.objects.filter(is_latest=True).order_by('-timestamp').first()
        
        if latest_data:
            # 한국 시간대 설정
            kst = pytz.timezone('Asia/Seoul')
            timestamp = latest_data.timestamp.astimezone(kst).strftime('%H:%M:%S')  # 24시간 형식
            
            # 자이로 센서 값으로 음주운전 상태 판단
            gyro_threshold = 10
            gyro_count = SensorData.objects.filter(
                device=latest_data.device,
                gyro__gte=gyro_threshold,
                timestamp__gte=latest_data.timestamp - timedelta(seconds=30)  # 최근 30초 동안의 데이터를 확인
            ).count()  # 최근 30초 동안 자이로 값이 4 이상인 횟수

            is_drunk_driving = gyro_count >= 10  # 3회 이상이면 음주운전 상태로 판단
            
            return JsonResponse({
                'status': 'success',
                'alcohol': latest_data.alcohol,
                'gyro': latest_data.gyro,
                'motor_speed': latest_data.motor_speed,
                'timestamp': timestamp,  # 포맷된 타임스탬프 반환
                'is_drunk_driving': is_drunk_driving #음주운전 상태 변수
            }) 
        else:
            return JsonResponse({'status': 'failure', 'message': 'No data available'}, status=404)
    
    return JsonResponse({'status': 'failure', 'message': 'Method not allowed'}, status=405)


# 최신 센서 데이터를 반환하는 뷰
@csrf_exempt
@require_http_methods(["POST"]) 
def get_sensor_data(request):
    if request.method == 'GET':
        latest_data = SensorData.objects.filter(is_latest=True).order_by('-timestamp').first()
        
        if latest_data:
            return JsonResponse({
                'status': 'success',
                'alcohol': latest_data.alcohol,
                'gyro': latest_data.gyro,
                'motor_speed': latest_data.motor_speed,
                'device': latest_data.device,
                'timestamp': str(latest_data.timestamp)
            })
        else:
            return JsonResponse({'status': 'failure', 'message': 'No data available'}, status=404)
    
    return JsonResponse({'status': 'failure', 'message': 'Method not allowed'}, status=405)
# 홈 페이지 뷰
def home(request):
    return HttpResponse("Hello from the main page!")

# 최신 데이터 표시 뷰
def display_latest_data(request):
    latest_data = SensorData.objects.filter(is_latest=True).order_by('-id')  # 최신 데이터 가져오기
    return render(request, 'sensor/latest_data.html', {'latest_data': latest_data})
