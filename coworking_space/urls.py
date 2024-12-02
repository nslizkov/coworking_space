from django.contrib import admin
from django.urls import path
from bookings import views as bookings_views
from bookings.views import DeviceListCreate, DeviceDetail, BookingListCreate, BookingDetail

urlpatterns = [
    path('', bookings_views.main, name='main'),
    path('register/', bookings_views.register, name='register'),
    path('devices/', bookings_views.device_list, name='device_list'),
    path('book/<int:device_id>/', bookings_views.book_device, name='book_device'),
    path('book/', bookings_views.book_device, name='book_device'),
    path('my-bookings/', bookings_views.user_bookings, name='user_bookings'),
    path('cancel_booking/<int:booking_id>/', bookings_views.cancel_booking, name='cancel_booking'),

    path('devices/delete/<int:device_id>/', bookings_views.delete_device, name='delete_device'),
    path('admin_page/', bookings_views.admin_page, name='admin_page'),
    path('admin/', admin.site.urls),
    path('add-device/', bookings_views.add_device, name='add_device'),
    path('admin_bookings/', bookings_views.admin_bookings, name='admin_bookings'),
    path('admin_bookings/delete/<int:booking_id>/', bookings_views.delete_booking, name='delete_booking'),


    path('api/devices/', DeviceListCreate.as_view(), name='device-list-create'),
    path('api/devices/<int:pk>/', DeviceDetail.as_view(), name='device-detail'),
    path('api/bookings/', BookingListCreate.as_view(), name='booking-list-create'),
    path('api/bookings/<int:pk>/', BookingDetail.as_view(), name='booking-detail'),
]
