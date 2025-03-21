from django.shortcuts import render

# 기존 뷰들
from django.http import JsonResponse, HttpResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
import json

# CSRF 토큰을 반환하는 뷰
@csrf_exempt
def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrf_token': csrf_token})

# CSRF 보호 해제 → ESP32에서 POST 요청 가능
@csrf_exempt  # CSRF 보호 해제
def receive_sensor_data(request):
    if request.method == 'POST':
        # 요청 본문이 비어 있거나 JSON 형식이 잘못된 경우 처리
        if not request.body:
            return JsonResponse({'status': 'failure', 'message': 'Empty request body'}, status=400)

        try:
            # 요청 본문을 디코딩하여 출력
            print(f"Request body: {request.body.decode('utf-8')}")

            # JSON 파싱
            data = json.loads(request.body)

            # 센서 값 추출
            sensor_value = data.get('sensor_value')

            if sensor_value is None:
                return JsonResponse({'status': 'failure', 'message': 'No sensor_value provided'}, status=400)

            # 받은 데이터 출력
            print(f"Received sensor value: {sensor_value}")
            print(f"Received data: {data}")

            # HTML 응답 생성
            html_response = f"""
            <html>
                <body>
                    <h1>Received Sensor Data</h1>
                    <p>Sensor Value: {sensor_value}</p>
                </body>
            </html>
            """
            return HttpResponse(html_response)

        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {str(e)}")
            return JsonResponse({'status': 'failure', 'message': 'Invalid JSON'}, status=400)

    return JsonResponse({'status': 'failure', 'message': 'Method not allowed'}, status=405)

# 홈 페이지 뷰
def home(request):
    return HttpResponse("Hello from the main page!")

# index 뷰 추가
