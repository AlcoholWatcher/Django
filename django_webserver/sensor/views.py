from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import SensorData  # SensorData 모델 임포트
from django.utils import timezone
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

# 최신 센서 데이터를 반환하는 뷰
@csrf_exempt
def get_latest_sensor_data(request):
    if request.method == 'GET':
        latest_data = SensorData.objects.filter(is_latest=True).order_by('-timestamp').first()
        
        if latest_data:
            # 한국 시간대 설정
            kst = pytz.timezone('Asia/Seoul')
            timestamp = latest_data.timestamp.astimezone(kst).strftime('%H:%M:%S')
            
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

            # 자이로 카운트 및 시작 시간 초기화
            gyro_count = cache.get(latest_data.device + '_gyro_count', 0)
            start_time = cache.get(latest_data.device + '_gyro_start_time', None)
            alert_sent = cache.get(latest_data.device + '_drunk_driving_alerted', False)

            # 현재 시간
            current_time = timezone.now()

            # 알콜 감지 상태 관리
            if alcohol_detected:
                cache.set(latest_data.device + '_drunk_driving_condition', 'Alcohol detection')

            # 자이로 값 체크 및 카운트 증가 (알콜 감지 상태일 때만)
            if drunk_driving_condition == 'Alcohol detection' and latest_data.gyro >= 100:  # 알콜 감지 상태일 때
                gyro_count += 1  # 카운트 증가
                print(f"Gyro count increased: {gyro_count}")  # 디버깅 로그 추가
                cache.set(latest_data.device + '_gyro_count', gyro_count, timeout=20)  # 카운트를 캐시에 저장 (20초 유지)

                # 시작 시간이 없으면 현재 시간으로 설정
                if start_time is None:
                    print("Setting start time")  # 디버깅 로그 추가
                    cache.set(latest_data.device + '_gyro_start_time', current_time, timeout=20)

            # 20초가 경과했는지 확인
            if start_time is not None:
                elapsed_time = (current_time - start_time).total_seconds()
                print(f"Elapsed time: {elapsed_time}")  # 디버깅 로그 추가
                if elapsed_time >= 20:
                    # 20초가 경과했으면 카운트 확인
                    if gyro_count >= 10 and not alert_sent:  # alert_sent 체크 (수정된 부분)
                        print("Sending True to ESP32")  # ESP32로 전송하는 로직
                        cache.set(latest_data.device + '_drunk_driving_alerted', True, timeout=60)  # 60초 동안 중복 전송 방지
                    else:
                        print("Not sending True to ESP32, count is less than 10 or already sent")  # 카운트가 10 미만일 경우

                    # 카운트와 시작 시간 초기화
                    cache.delete(latest_data.device + '_gyro_count')
                    cache.delete(latest_data.device + '_gyro_start_time')
            # JSON 응답 반환
            return JsonResponse({
                'status': 'success',
                'alcohol': latest_data.alcohol,
                'gyro': latest_data.gyro,
                'motor_speed': latest_data.motor_speed,
                'gyro_count': gyro_count,
                'timestamp': timestamp,
                'condition': drunk_driving_condition,
                'motor_speed_condition': motor_speed_condition,
                'is_drunk_driving': gyro_count >= 10  # 카운트가 10 이상일 때 True
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
