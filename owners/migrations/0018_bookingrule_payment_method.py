# Generated by Django 5.1.3 on 2024-12-08 05:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('owners', '0017_alter_house_house_name'),
        ('settings', '0004_alter_payment_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingrule',
            name='payment_method',
            field=models.ForeignKey(blank=True, help_text='The payment method that will be used during booking.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='booking_rules', to='settings.payment', verbose_name='Payment Method'),
        ),
    ]
