# Generated by Django 4.2 on 2023-05-02 22:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reservationSystem', '0013_remove_room_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservation',
            name='user',
        ),
    ]
