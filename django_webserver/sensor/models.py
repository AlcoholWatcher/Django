# sensor/models.py
from django.db import models

class SensorData(models.Model):
    device = models.CharField(max_length=50)
    sensor_value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device} - {self.sensor_value} at {self.timestamp}"
