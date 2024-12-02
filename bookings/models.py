from django.db import models
from django.contrib.auth.models import User

class Device(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    available_times = models.JSONField(default=list)

    def __str__(self):
        return self.name

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    booking_time = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username}: {self.device.name} at {self.booking_time}"

