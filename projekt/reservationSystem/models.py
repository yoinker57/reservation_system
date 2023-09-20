from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    name = models.CharField('Room name' ,max_length=255)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Equipment(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    capacity = models.IntegerField('Capacity')
    projector = models.BooleanField(default=False)
    WiFi = models.BooleanField(default=False)
    computers = models.BooleanField(default=False)
    start_date = models.DateField(null=False, blank=True)
    end_date = models.DateField(null=False, blank=True)
    
    
class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    comment = models.TextField(blank=True)
    email_adress = models.EmailField('Email adress')


    def __str__(self):
        return f'{self.room} {self.date} {self.start_time}'