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
@csrf_exempt
def receive_sensor_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            sensor_value = data.get('sensor_value')

            if sensor_value is None:
                return JsonResponse({'status': 'failure', 'message': 'No sensor_value provided'}, status=400)

            print(f"Received sensor value: {sensor_value}")
            print(f"Received data: {data}")  # 디버깅용으로 요청 데이터를 출력

            html_response = f"""
            <html>
                <body>
                    <h1>Received Sensor Data</h1>
                    <p>Sensor Value: {sensor_value}</p>
                </body>
            </html>
            """
            return HttpResponse(html_response)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'failure', 'message': 'Invalid JSON'}, status=400)

    return JsonResponse({'status': 'failure', 'message': 'Method not allowed'}, status=405)

# 홈 페이지 뷰
def home(request):
    return HttpResponse("Hello from the main page!")

# index 뷰 추가
def index(request):
    return render(request, 'sensor/index.html')
