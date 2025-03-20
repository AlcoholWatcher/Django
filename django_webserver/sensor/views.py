# sensor/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# 알콜 센서 데이터를 받는 POST 요청을 처리하는 뷰
@csrf_exempt
def receive_sensor_data(request):
    if request.method == 'POST':
        data = json.loads(request.body)  # 요청 본문에서 JSON 데이터 읽기
        sensor_value = data.get('sensor_value', None)
        
        # 데이터가 있으면 출력, 저장 등의 처리를 추가
        print(f"Received sensor value: {sensor_value}")
        
        # 데이터베이스에 저장하려면 모델을 사용
        # AlcoholSensorData.objects.create(sensor_value=sensor_value)
        
        return JsonResponse({'status': 'success', 'sensor_value': sensor_value})

    return JsonResponse({'status': 'failure'})
