from django.contrib import admin

from .models import Device

'''
@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'available')
    search_fields = ('name',)
'''

from django.contrib import admin
from .models import Device, Booking

class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_available')  # Измените на is_available
    search_fields = ('name',)

    def is_available(self, obj):
        return bool(obj.available_times)  # Проверяем, есть ли доступные временные интервалы

    is_available.boolean = True  # Отображаем как булевое значение (галочка или крестик)
    is_available.short_description = 'Available'  # Заголовок столбца

class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'device', 'booking_time')  # Отображаем записи
    ordering = ('booking_time',)  # Сортируем по времени записи

admin.site.register(Device, DeviceAdmin)
admin.site.register(Booking, BookingAdmin)
