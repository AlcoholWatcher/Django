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
from django.core.cache import cache
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
from django.core.cache import cache

@csrf_exempt
def get_latest_sensor_data(request):
    if request.method == 'GET':
        latest_data = SensorData.objects.filter(is_latest=True).order_by('-timestamp').first()
        
        if latest_data:
            # 한국 시간대 설정
            kst = pytz.timezone('Asia/Seoul')
            timestamp = latest_data.timestamp.astimezone(kst).strftime('%H:%M:%S')  # 24시간 형식
            
            # 알콜 센서 값 체크
            alcohol_threshold = 100
            alcohol_detected = latest_data.alcohol >= alcohol_threshold
            
            # 상태 캐시에서 가져오기
            drunk_driving_condition = cache.get(latest_data.device + '_drunk_driving_condition', 'Normal')
            motor_speed_condition = cache.get(latest_data.device + '_motor_speed_condition', 'Driving')

            # 모터 스피드 상태 업데이트
            if latest_data.motor_speed >= 500:
                motor_speed_condition = 'Driving'
            elif latest_data.motor_speed < 500 and latest_data.motor_speed > 0:
                motor_speed_condition = 'Slowing down'
            elif latest_data.motor_speed <= 0:
                motor_speed_condition = 'Stop'

            # 상태를 캐시에 저장
            cache.set(latest_data.device + '_motor_speed_condition', motor_speed_condition)

            # 알콜 감지 시 자이로 센서 카운트 증가
            gyro_threshold = 100
            start_time = latest_data.timestamp - timedelta(seconds=20)
            gyro_count = cache.get(latest_data.device + '_gyro_count', 0)  # 기본값 0

            if drunk_driving_condition == 'Alcohol detection':
                # 자이로 센서 카운트 증가
                if latest_data.gyro >= gyro_threshold:
                    gyro_count += 1  # 카운트 증가

                # 카운트를 캐시에 저장
                cache.set(latest_data.device + '_gyro_count', gyro_count, timeout=20)  # 20초 유지

                # 자이로 센서 조건 확인
                is_drunk_driving = gyro_count >= 10  # 10회 이상이면 음주운전 상태로 판단

                # ESP32로 전송하는 로직 (여기에 예시로 print를 사용, 실제로는 ESP32로 전송하는 코드로 대체)
                if is_drunk_driving:
                    if not cache.get(latest_data.device + '_drunk_driving_alerted', False):
                        print("Sending True to ESP32")  # 실제 ESP32로 전송하는 로직으로 변경 필요
                        cache.set(latest_data.device + '_drunk_driving_alerted', True, timeout=60)  # 60초 동안 중복 전송 방지

            else:
                # 알콜 감지되지 않으면 자이로 카운트 초기화
                cache.delete(latest_data.device + '_gyro_count')
                cache.delete(latest_data.device + '_drunk_driving_alerted')

            return JsonResponse({
                'status': 'success',
                'alcohol': latest_data.alcohol,
                'gyro': latest_data.gyro,
                'motor_speed': latest_data.motor_speed,
                'gyro_count': gyro_count,  # gyro_count 값 추가
                'timestamp': timestamp,
                'condition': drunk_driving_condition,  # Condition 추가
                'motor_speed_condition': motor_speed_condition,  # 모터 스피드 상태 추가
                'is_drunk_driving': is_drunk_driving if drunk_driving_condition == 'suspected drunk driving' else False
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
