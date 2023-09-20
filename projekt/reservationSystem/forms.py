from django.db import models
from django import forms
from django.forms import ModelForm, Form
from .models import Reservation, Room, Equipment
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ReservationFilterForm(Form):
    CHOICES = [
        (None, '---------'),
        (True, 'Tak'),
        (False, 'Nie'),
    ]
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), required=False)
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), required=False)
    wifi = forms.CharField(widget=forms.Select(choices=CHOICES), required=False)
    projector = forms.CharField(widget=forms.Select(choices=CHOICES), required=False)
    computers = forms.CharField(widget=forms.Select(choices=CHOICES), required=False)
    min_capacity = forms.IntegerField(widget=forms.NumberInput(attrs={'type': 'number'}), required=False)
    max_capacity = forms.IntegerField(widget=forms.NumberInput(attrs={'type': 'number'}), required=False)

class ReservationForm(ModelForm):
    comment = forms.CharField(widget=forms.Textarea(attrs={'rows': 2, 'cols': 50}), required=False)
    class Meta:
        model = Reservation
        fields = ['date', 'start_time', 'end_time', 'comment', 'email_adress']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'comment': forms.Textarea(attrs={'rows': 2, 'cols': 50}),
            'email_adress': forms.EmailInput(attrs={'type': 'email'}),
        }


class RoomAndEquipment(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.CharField(max_length=100)
    capacity = models.IntegerField()
    name = models.CharField(max_length=100)
    WiFi = models.BooleanField()
    computers = models.BooleanField()
    projector = models.BooleanField()


class RoomForm(ModelForm):
    class Meta:
        CHOICES = [
            (None, '---------'),
            (True, 'Tak'),
            (False, 'Nie'),
        ]
        model = RoomAndEquipment
        fields = ['name', 'capacity', 'WiFi', 'projector', 'computers', 'description', 'start_date', 'end_date']
        widgets = {
            'name': forms.TextInput(attrs={'type': 'text'},),
            'capacity': forms.NumberInput(attrs={'type': 'number'}),
            'WiFi': forms.Select(choices=CHOICES),
            'projector': forms.Select(choices=CHOICES),
            'computers': forms.Select(choices=CHOICES),
            'description': forms.Textarea(attrs={'rows': 2, 'cols': 50}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

        # def clean(self):
        #     cleaned_data = super().clean()
        #     name = cleaned_data.get('name')
        #     capacity = cleaned_data.get('capacity')
        #     WiFi = cleaned_data.get('WiFi')
        #     projector = cleaned_data.get('projector')

        #     if not name or not capacity or WiFi is None or projector is None:
        #         raise forms.ValidationError("Wszystkie pola są wymagane.")

        #     return cleaned_data
        
class DeleteForm(forms.Form):
    delete_button = forms.CharField(widget=forms.HiddenInput())