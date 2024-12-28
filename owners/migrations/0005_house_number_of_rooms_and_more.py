# Generated by Django 5.1.3 on 2024-12-03 16:15

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('owners', '0004_remove_room_photo1_remove_room_photo2_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='house',
            name='number_of_rooms',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Number of Rooms'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='house',
            name='proximity_information',
            field=models.JSONField(blank=True, verbose_name='Proximity Information (e.g., Schools, Hospitals)'),
        ),
        migrations.AlterField(
            model_name='house',
            name='utilities_included',
            field=models.TextField(blank=True, verbose_name='Utilities Included in Rent'),
        ),
        migrations.AlterField(
            model_name='roomphoto',
            name='photo',
            field=models.ImageField(upload_to='room_photos/', verbose_name='Room Photo'),
        ),
        migrations.AlterField(
            model_name='roomphoto',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='owners.room', verbose_name='Room'),
        ),
    ]