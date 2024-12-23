# Generated by Django 5.1.3 on 2024-12-03 16:03

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('owners', '0003_remove_room_photo_1_remove_room_photo_2_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='photo1',
        ),
        migrations.RemoveField(
            model_name='room',
            name='photo2',
        ),
        migrations.RemoveField(
            model_name='room',
            name='photo3',
        ),
        migrations.RemoveField(
            model_name='room',
            name='room_description',
        ),
        migrations.RemoveField(
            model_name='room',
            name='video',
        ),
        migrations.AddField(
            model_name='room',
            name='description',
            field=models.TextField(blank=True, verbose_name='Room Description'),
        ),
        migrations.AddField(
            model_name='room',
            name='room_number',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Room Number'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='room',
            name='room_video',
            field=models.FileField(blank=True, null=True, upload_to='room_videos/', verbose_name='Room Video'),
        ),
        migrations.AlterField(
            model_name='room',
            name='availability_status',
            field=models.CharField(choices=[('Available', 'Available'), ('Occupied', 'Occupied')], default='Available', max_length=20, verbose_name='Availability Status'),
        ),
        migrations.AlterField(
            model_name='room',
            name='house',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rooms', to='owners.house', verbose_name='House'),
        ),
        migrations.AlterField(
            model_name='room',
            name='rental_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Rental Price (Monthly/Yearly)'),
        ),
        migrations.CreateModel(
            name='RoomPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(upload_to='room_photos/')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='owners.room')),
            ],
        ),
    ]
