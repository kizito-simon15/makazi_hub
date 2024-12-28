# Generated by Django 5.1.3 on 2024-12-16 18:12

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0010_houselocation'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='houselocation',
            options={},
        ),
        migrations.AlterField(
            model_name='houselocation',
            name='altitude',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Altitude in meters.', max_digits=7, null=True),
        ),
        migrations.AlterField(
            model_name='houselocation',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, validators=[django.core.validators.MinValueValidator(-90.0), django.core.validators.MaxValueValidator(90.0)]),
        ),
        migrations.AlterField(
            model_name='houselocation',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, validators=[django.core.validators.MinValueValidator(-180.0), django.core.validators.MaxValueValidator(180.0)]),
        ),
    ]
