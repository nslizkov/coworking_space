# Generated by Django 5.1.3 on 2024-12-01 13:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0003_userprofile'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]
