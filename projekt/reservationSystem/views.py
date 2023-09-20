import datetime
from time import sleep
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .forms import RegistrationForm, ReservationFilterForm, ReservationForm, RoomForm
from reservationSystem.models import Room, Reservation
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Equipment, Room

# def register_view(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Rejestracja zakończona sukcesem. Możesz się teraz zalogować.')
#             return redirect('login')
#     else:
#         form = UserCreationForm()
#     return render(request, 'register.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            # Tworzenie nowego użytkownika
            user = form.save(commit=False)
            user.email = email
            user.save()
            messages.success(request, 'Rejestracja zakończona sukcesem. Możesz się teraz zalogować.')
            return redirect('login')  
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Nieprawidłowe dane logowania.')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    print('logout')
    return redirect('login')



def home(request):
    room_list = []
    form = ReservationFilterForm(request.POST)
    if request.method == 'POST':
        query = Q()
        if form.is_valid():
            date = request.POST['date']
            if date < str(datetime.date.today()) and date != '':
                messages.error(request, 'Nie można zarezerwować pokoju w przeszłości.')
                return render(request, 'home.html', {'form': form})
            request.session['date'] = date
            start_time = request.POST['start_time']
            request.session['start_time'] = start_time
            end_time = request.POST['end_time']
            if start_time >= end_time and start_time != '' and end_time != '':
                messages.error(request, 'Godzina rozpoczęcia musi być wcześniejsza od godziny zakończenia.')
                return render(request, 'home.html', {'form': form})
            request.session['end_time'] = end_time
            wifi = request.POST.get('wifi', None)
            projector = request.POST.get('projector', None)
            computers = request.POST.get('computers', None)
            min_capacity = request.POST['min_capacity']
            max_capacity = request.POST['max_capacity']
            if min_capacity != '' and max_capacity != '' and (int(min_capacity) < 0 or int(max_capacity) < 0):
                messages.error(request, 'Pojemność sali nie może być ujemna.')
                return render(request, 'home.html', {'form': form})
            if min_capacity == '':
                min_capacity = 0
            if max_capacity == '':
                max_capacity = 10**10
            
            if min_capacity:
                query &= Q(equipment__capacity__gte=min_capacity)
            if max_capacity:
                query &= Q(equipment__capacity__lte=max_capacity)
            if wifi:
                if wifi == 'True':
                    query &= Q(equipment__WiFi=True)
                else:
                    query &= Q(equipment__WiFi=False)
            if projector:
                if projector == 'True':
                    query &= Q(equipment__projector=True)
                else:
                    query &= Q(equipment__projector=False)
            if computers:
                if computers == 'True':
                    query &= Q(equipment__computers=True)
                else:
                    query &= Q(equipment__computers=False)
            # if date:
            #     query &= ~Q(reservation__date=date)
            if date:
                query &= Q(equipment__start_date__lte=date, equipment__end_date__gte=date)
            if start_time:
                query &= ~Q(reservation__start_time__lte=start_time, reservation__end_time__gte=start_time, reservation__date=date)
            if end_time:
                query &= ~Q(reservation__start_time__lte=end_time, reservation__end_time__gte=end_time, reservation__date=date)
            if start_time and end_time:
                query &= ~Q(reservation__start_time__gte=start_time, reservation__end_time__lte=end_time, reservation__date=date)
            room_list = Room.objects.filter(query).values('name', 'description', 'equipment__capacity', 'equipment__projector', 'equipment__WiFi', 'equipment__computers', 'equipment__start_date', 'equipment__end_date', 'id')
    print(room_list)

    context = {
        'room_list': room_list,
        'form': form,
    }
    return render(request, 'home.html', context)

def AddReservation(request):
    return render(request, 'add_reservation.html')

def room(request, roomId):
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        room = Room.objects.get(id=roomId)
    except Room.DoesNotExist:
        return home(request)
    date = request.session.get('date', None)
    start_time = request.session.get('start_time', None)
    end_time = request.session.get('end_time', None)
    email = request.user.email
    form = ReservationForm(request.POST or None, initial={'date': date, 'start_time': start_time, 'end_time': end_time, 'email_adress': email})
    context = {
        'room': room,
        'form': form,
    }
    if request.method == 'POST':
        if form.is_valid():
            date = request.POST['date']
            if date < str(datetime.date.today()):
                messages.error(request, 'Nie można zarezerwować pokoju w przeszłości.')
                return render(request, 'room.html', context)
            start_time = request.POST['start_time']
            end_time = request.POST['end_time']
            if start_time >= end_time:
                messages.error(request, 'Godzina rozpoczęcia musi być wcześniejsza od godziny zakończenia.')
                return render(request, 'room.html', context)
            comment = request.POST['comment']
            email_adress = request.POST['email_adress']
            user = request.user
            if not checkroom(room, date, start_time, end_time):
                messages.error(request, 'Pokój jest już zarezerwowany w tym terminie.')
            else:
                reservation = Reservation.objects.create(date=date, start_time=start_time, end_time=end_time, comment=comment, email_adress=email_adress, room=room, user=user)
                reservation.save()
                return redirect('succesfullReservation')
    return render(request, 'room.html', context)

def checkroom(room, date, start_time, end_time):
    reservations = Reservation.objects.filter(room=room, date=date)
    reservations = reservations.filter(
    Q(start_time__lte=start_time, end_time__gte=start_time) |
    Q(start_time__lte=end_time, end_time__gte=end_time) |
    Q(start_time__gte=start_time, end_time__lte=end_time) |
    Q(start_time__lte=start_time, end_time__gte=end_time)
    )   
    if reservations:
        return False
    return True

def checkroom2(room, date, start_time, end_time, reservation_id):
    reservations = Reservation.objects.filter(room=room, date=date).exclude(id=reservation_id)
    reservations = reservations.filter(
        Q(start_time__lte=start_time, end_time__gte=start_time) |
        Q(start_time__lte=end_time, end_time__gte=end_time) |
        Q(start_time__gte=start_time, end_time__lte=end_time) |
        Q(start_time__lte=start_time, end_time__gte=end_time)
    )
    if reservations:
        return False
    return True

def succesfullReservation(request):
    return render(request, 'succesfullReservation.html')

def succesfullDelated(request):
    return render(request, 'succesfullDelated.html')

def adminPanel(request):
    return render(request, 'adminPanel.html')

def rooms(request):
    rooms = Room.objects.all()
    context = {
        'room_list': rooms,
    }
    return render(request, 'rooms.html', context)

def roomDetails(request, roomId):
    equipments = Equipment.objects.filter(room=roomId)
    context = {
        'equipment_list': equipments,
        'roomId': roomId,
    }
    return render(request, 'roomDetails.html', context)

def reservations(request):
    reservations = Reservation.objects.all()
    context = {
        'reservations_list': reservations,
    }
    if request.method == 'POST':
        if 'delete_button' in request.POST:
            reservation_id = request.POST.get('reservation_id')
            print(reservation_id)
            reservation = Reservation.objects.get(id=reservation_id)
            reservation.delete()
            return redirect('reservations')
    return render(request, 'reservations.html', context)

def reservation(request, reservationId):
    try:
        reservation = Reservation.objects.get(id=reservationId)
    except Reservation.DoesNotExist:
        return redirect('reservations')

    form = ReservationForm(request.POST or None, initial={'date': reservation.date, 'start_time': reservation.start_time, 'end_time': reservation.end_time, "comment": reservation.comment, "email_adress": reservation.email_adress})

    context = {
        'form': form,
        'reservation': reservation,
    }

    if request.method == 'POST':
        if 'delete_button' in request.POST:
            reservation.delete()
            return redirect('succesfullDelated')
        date = request.POST['date']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        if start_time >= end_time:
            messages.error(request, 'Godzina rozpoczęcia musi być wcześniejsza od godziny zakończenia.')
            return render(request, 'room.html', context)
        comment = request.POST['comment']
        email_adress = request.POST['email_adress']
        if not checkroom2(reservation.room.id, date, start_time, end_time, reservation.id):
            messages.error(request, 'Pokój jest już zarezerwowany w tym terminie.')
        else:
            reservation.date = date
            reservation.start_time = start_time
            reservation.end_time = end_time
            reservation.comment = comment
            reservation.email_adress = email_adress
            reservation.save()
            return redirect('succesfullReservation')

    return render(request, 'reservation.html', context)




def addRoom(request):
    form = RoomForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            name = request.POST['name']
            capacity = request.POST['capacity']
            if int(capacity) <= 0:
                messages.error(request, 'Pojemność musi być większa od 0.')
                return render(request, 'addRoom.html', {'form': form})
            WiFi = request.POST.get('WiFi', None)
            projector = request.POST.get('projector', None)
            computers = request.POST.get('computers', None)
            if WiFi == "" or projector == "" or computers == "":
                messages.error(request, 'Musisz wybrać jedną z opcji Tak/Nie.')
                return render(request, 'addRoom.html', {'form': form})
            description = request.POST['description']
            start_date = request.POST['start_date']
            end_date = request.POST['end_date']
            if start_date >= end_date:
                messages.error(request, 'Data rozpoczęcia musi być wcześniejsza od daty zakończenia.')
                return render(request, 'addRoom.html', {'form': form})
            room = Room.objects.create(name=name, description=description)
            equipment = Equipment.objects.create(room=room, capacity=capacity, WiFi=WiFi, projector=projector,
                                                computers=computers, start_date=start_date, end_date=end_date)
            room.save()
            equipment.save()
            return redirect('rooms')
    context = {
        'form': form,
    }
    return render(request, 'addRoom.html', context)

def editRoom(request, roomId):
    # try:
    #     room = Equipment.objects.filter(room=roomId)
    # except Room.DoesNotExist:
    #     return redirect('rooms')
   
    form = RoomForm(request.POST or None)#, initial={'name': room.name, 'capacity': room.capacity, 'WiFi': room.WiFi, 'projector': room.projector,
                                          #         'computers': room.computers, 'description': room.description, 'start_date': room.start_date, 'end_date': room.end_date})
    if request.method == 'POST':
        if form.is_valid():
            name = request.POST['name']
            capacity = request.POST['capacity']
            if int(capacity) <= 0:
                messages.error(request, 'Pojemność musi być większa od 0.')
                return render(request, 'editRoom.html', {'form': form})
            WiFi = request.POST.get('WiFi', None)
            projector = request.POST.get('projector', None)
            computers = request.POST.get('computers', None)
            if WiFi == "" or projector == "" or computers == "":
                messages.error(request, 'Musisz wybrać jedną z opcji Tak/Nie.')
                return render(request, 'editRoom.html', {'form': form})
            description = request.POST['description']
            start_date = request.POST['start_date']
            end_date = request.POST['end_date']
            if start_date >= end_date:
                messages.error(request, 'Data rozpoczęcia musi być wcześniejsza od daty zakończenia.')
                return render(request, 'editRoom.html', {'form': form})
            room = Room.objects.get(id=roomId)
            room.name = name
            room.description = description
            equipment = Equipment.objects.create(room=room, capacity=capacity, WiFi=WiFi, projector=projector,
                                                  computers=computers, start_date=start_date, end_date=end_date)
            room.save()
            equipment.save()
            return redirect('rooms')
    context = {
        'form': form,
    }
    return render(request, 'editRoom.html', context)

def delete_room(request, roomId):
    try:
        room = Room.objects.get(id=roomId)
    except Room.DoesNotExist:
        return redirect('rooms')
    
    # equipment = Equipment.objects.filter(room=room)
    # for e in equipment:
    #     e.delete()
    room.delete()
    return redirect('rooms')

def deleteEquipment(request, equipmentId):
    try:
        equipment = Equipment.objects.get(id=equipmentId)
        roomId = equipment.room.id
    except Equipment.DoesNotExist:
        return redirect('rooms')
    equipment.delete()
    return redirect('roomDetails', roomId)

def handle_404(request, exception):
    return render(request, '404.html', status=404)

