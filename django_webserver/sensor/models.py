# sensor/models.py
from django.db import models

class SensorData(models.Model):
    device = models.CharField(max_length=100)
    alcohol = models.IntegerField()
    gyro = models.IntegerField()
    motor_speed = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_latest = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.device}: {self.sensor_value} at {self.timestamp}"
