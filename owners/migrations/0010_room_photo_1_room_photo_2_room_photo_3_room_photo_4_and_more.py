# Generated by Django 5.1.3 on 2024-12-04 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('owners', '0009_alter_house_amenities_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='photo_1',
            field=models.ImageField(blank=True, null=True, upload_to='room_photos/', verbose_name='Photo 1'),
        ),
        migrations.AddField(
            model_name='room',
            name='photo_2',
            field=models.ImageField(blank=True, null=True, upload_to='room_photos/', verbose_name='Photo 2'),
        ),
        migrations.AddField(
            model_name='room',
            name='photo_3',
            field=models.ImageField(blank=True, null=True, upload_to='room_photos/', verbose_name='Photo 3'),
        ),
        migrations.AddField(
            model_name='room',
            name='photo_4',
            field=models.ImageField(blank=True, null=True, upload_to='room_photos/', verbose_name='Photo 4'),
        ),
        migrations.AddField(
            model_name='room',
            name='photo_5',
            field=models.ImageField(blank=True, null=True, upload_to='room_photos/', verbose_name='Photo 5'),
        ),
        migrations.DeleteModel(
            name='RoomPhoto',
        ),
    ]