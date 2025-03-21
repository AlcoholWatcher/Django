# sensor/models.py
from django.db import models

class SensorData(models.Model):
    device = models.CharField(max_length=50)
    sensor_value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_latest = models.BooleanField(default=False)  # 최신 데이터 여부

    def __str__(self):
        return f"{self.device}: {self.sensor_value} at {self.timestamp}"
