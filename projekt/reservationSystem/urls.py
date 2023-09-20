from django.urls import path
from django.contrib import admin
from . import views
from django.conf.urls import handler404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required


def staff_check(user):
    return user.is_staff

def admin_panel_view(request):
    if not request.user.is_staff:
        return redirect('/reservationSystem/')
    return render(request, 'adminPanel.html')

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('room/<int:roomId>', views.room, name='room'),
    path('succesfullReservation/', views.succesfullReservation, name='succesfullReservation'),
    path('succesfullDelated/', views.succesfullDelated, name='succesfullDelated'),
    path('adminPanel/', admin_panel_view, name='adminPanel'),
    path('adminPanel/rooms/', views.rooms, name='rooms'),
    path('adminPanel/addRoom/', views.addRoom, name='addRoom'),
    path('adminPanel/roomDetails/<int:roomId>', views.roomDetails, name='roomDetails'),
    path('adminPanel/editRoom/<int:roomId>', views.editRoom, name='editRoom'),
    path('adminPanel/deleteRoom/<int:roomId>', views.delete_room, name='deleteRoom'),
    path('adminPanel/deleteEquipment/<int:equipmentId>', views.deleteEquipment, name='deleteEquipment'),
    path('adminPanel/reservations/', views.reservations, name='reservations'),
    path('adminPanel/reservations/<int:reservationId>', views.reservation, name='reservation'),
    path('', views.home, name='home'),
]

handler404 = views.handle_404