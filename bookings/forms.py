from django import forms
from .models import Booking
from .models import Device
from datetime import datetime, timedelta

def generate_time_slots(start_time, end_time):
    slots = []
    current_time = start_time
    while current_time < end_time:
        slots.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=30)
    return slots

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['device', 'booking_time']

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['name', 'description', 'available_times']

    available_times = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=[(time, time) for time in generate_time_slots(datetime.now().replace(hour=9, minute=0), datetime.now().replace(hour=17, minute=0))],
        label="Доступные временные интервалы"
    )