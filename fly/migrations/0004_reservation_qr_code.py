# Generated by Django 5.1.4 on 2025-01-15 20:40

import fly.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fly', '0003_flight_flight_class'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='qr_code',
            field=models.ImageField(blank=True, null=True, upload_to=fly.models.upload_ticket),
        ),
    ]
