from django.http import JsonResponse
from django.shortcuts import render

def control_led(request):
    action = request.GET.get('action', '')
    if action == 'on':
        # 실제 LED 제어 코드 추가 (예: GPIO 핀을 사용하여 LED를 켜는 코드)
        return JsonResponse({"status": "LED ON"})
    elif action == 'off':
        # 실제 LED 제어 코드 추가 (예: GPIO 핀을 사용하여 LED를 끄는 코드)
        return JsonResponse({"status": "LED OFF"})
    else:
        return JsonResponse({"error": "Invalid action"})

def home(request):
    # 홈 페이지에 버튼을 포함한 HTML 반환
    return render(request, 'home.html')