# Generated by Django 5.1.7 on 2025-04-05 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0002_stadium'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('status', models.CharField(choices=[('booked', 'Đã đặt'), ('canceled', 'Đã hủy')], default='booked', max_length=20)),
            ],
        ),
    ]
