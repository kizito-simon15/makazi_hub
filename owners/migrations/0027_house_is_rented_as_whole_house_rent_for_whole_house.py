# Generated by Django 5.1.3 on 2024-12-26 16:47

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('owners', '0026_house_is_trending'),
    ]

    operations = [
        migrations.AddField(
            model_name='house',
            name='is_rented_as_whole',
            field=models.BooleanField(default=False, verbose_name='Is your house rented as a whole?'),
        ),
        migrations.AddField(
            model_name='house',
            name='rent_for_whole_house',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Rent for the Whole House'),
        ),
    ]
