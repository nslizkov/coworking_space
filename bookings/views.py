from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required

from .models import Device, Booking
from .forms import DeviceForm
from .serializers import DeviceSerializer, BookingSerializer

from rest_framework import generics
from datetime import timedelta, datetime


def get_available_time_slots(device):
    available_slots = []
    now = timezone.now() + timedelta(hours=3)  # Добавляем 3 часа
    start_date = now.date()
    end_date = start_date + timedelta(days=3)

    bookings = Booking.objects.filter(device=device, booking_time__date__range=(start_date, end_date)).order_by(
        'booking_time')
    available_times = [datetime.strptime(time, "%H:%M").time() for time in device.available_times]

    for single_date in (start_date + timedelta(n) for n in range(3)):
        for time in available_times:
            current_datetime_start = timezone.make_aware(datetime.combine(single_date, time))
            current_datetime_end = timezone.make_aware(
                datetime.combine(single_date, (datetime.combine(single_date, time) + timedelta(minutes=30)).time())
            )

            # Проверяем, что слот находится в будущем
            if current_datetime_start > now:
                is_booked = any(
                    current_datetime_start <= booking.booking_time < current_datetime_end
                    for booking in bookings
                )
                if not is_booked:
                    available_slots.append((current_datetime_start.strftime("%Y-%m-%d %H:%M"),
                                            current_datetime_end.strftime("%Y-%m-%d %H:%M")))
                else:
                    print(f"Слот занят: {current_datetime_start} - {current_datetime_end}")

    if not available_slots:
        print("Нет доступных слотов.")

    return available_slots


def format_remaining_time(booking_time):
    if not isinstance(booking_time, datetime):
        raise ValueError("booking_time должен быть объектом datetime")
    now = datetime.now()
    remaining_time = booking_time - now
    if remaining_time.total_seconds() < 0:
        remaining_time_str = "Время прошло"
    else:
        days, seconds = remaining_time.days, remaining_time.seconds
        hours, minutes = divmod(seconds, 60)
        remaining_time_str = f"Осталось: {days} дня(ей), {hours} часа(ов), {minutes} минут(ы)"

    formatted_date = booking_time.strftime("%-d.%m.%Y %H:%M")

    return f"{formatted_date} ({remaining_time_str})"


def main(request):
    return render(request, 'main.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('main')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('main')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})



@login_required
def device_list(request):
    devices = Device.objects.all()
    is_admin = request.user.is_staff  # Проверка, является ли пользователь администратором
    return render(request, 'device_list.html', {'devices': devices, 'is_admin': is_admin})

def delete_device(request, device_id):
    device = get_object_or_404(Device, id=device_id)
    Booking.objects.filter(device=device).delete()
    device.delete()
    return redirect('device_list')

@login_required
def book_device(request, device_id):
    device = get_object_or_404(Device, id=device_id)
    available_slots = get_available_time_slots(device)

    if request.method == 'POST':
        selected_times = request.POST.getlist('time')
        for time in selected_times:
            booking_time = timezone.datetime.strptime(time, "%Y-%m-%d %H:%M")
            Booking.objects.create(user=request.user, device=device, booking_time=booking_time)
        return redirect('user_bookings')

    return render(request, 'book_device.html', {'device': device, 'available_slots': available_slots})


@login_required
def user_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('booking_time')
    return render(request, 'user_bookings.html', {'bookings': bookings})


def format_remaining_time(booking_time):
    now = timezone.now()
    remaining_time = booking_time - now
    if remaining_time.total_seconds() < 0:
        return "Запись уже прошла"
    days, remainder = divmod(remaining_time.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)

    remaining_parts = []
    if days > 0:
        remaining_parts.append(f"{int(days)} день" + ("а" if days > 1 else ""))
    if hours > 0:
        remaining_parts.append(f"{int(hours)} час" + ("а" if hours > 1 else ""))
    if minutes > 0:
        remaining_parts.append(f"{int(minutes)} минут" + ("ы" if minutes > 1 else ""))

    return ", ".join(remaining_parts)


@login_required
def user_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    output_lines = []

    for booking in bookings:
        device_name = booking.device.name
        booking_time = booking.booking_time
        remaining_time = format_remaining_time(booking_time)

        output_lines.append(f"{device_name} - {booking_time.strftime('%d %B %Y, %I %p')} (осталось: {remaining_time})")

    return render(request, 'user_bookings.html', {'output_lines': output_lines})


@staff_member_required
def admin_page(request):
    return render(request, 'admin_page.html')


@staff_member_required
def add_device(request):
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            device = form.save(commit=False)
            device.available_times = form.cleaned_data['available_times']
            device.save()
            return redirect('device_list')
    else:
        form = DeviceForm()
    return render(request, 'add_device.html', {'form': form})


@staff_member_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.delete()
    return redirect('admin_bookings')


@staff_member_required
def admin_bookings(request):
    bookings = Booking.objects.all()
    output_lines = []
    for booking in bookings:
        device_name = booking.device.name
        booking_time = booking.booking_time
        remaining_time = format_remaining_time(booking_time)
        user_name = booking.user.username
        output_lines.append({
            'device_name': device_name,
            'booking_time': booking_time.strftime('%d %B %Y, %I %p'),
            'remaining_time': remaining_time,
            'user_name': user_name,
            'id': booking.id  # Сохраняем ID для удаления
        })
    return render(request, 'admin_bookings.html', {'output_lines': output_lines})


class DeviceListCreate(generics.ListCreateAPIView):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer


class DeviceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer


class BookingListCreate(generics.ListCreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer


class BookingDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
