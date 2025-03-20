from django.http import JsonResponse, HttpResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.utils.decorators import method_decorator
import json

# CSRF 토큰을 반환하는 뷰
@csrf_exempt  # CSRF 보호를 해제하여 CSRF 토큰을 발급받을 수 있도록 함
def get_csrf_token(request):
    csrf_token = get_token(request)  # CSRF 토큰 가져오기
    return JsonResponse({'csrf_token': csrf_token})  # CSRF 토큰을 JSON 형식으로 반환

@method_decorator(csrf_protect, name='dispatch')
def receive_sensor_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # 요청 본문에서 JSON 데이터 읽기
            sensor_value = data.get('sensor_value')

            if sensor_value is None:
                return JsonResponse({'status': 'failure', 'message': 'No sensor_value provided'}, status=400)

            print(f"Received sensor value: {sensor_value}")

            return JsonResponse({'status': 'success', 'sensor_value': sensor_value})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'failure', 'message': 'Invalid JSON'}, status=400)

    return JsonResponse({'status': 'failure', 'message': 'Method not allowed'}, status=405)

def home(request):
    return HttpResponse("Hello from the main page!")
