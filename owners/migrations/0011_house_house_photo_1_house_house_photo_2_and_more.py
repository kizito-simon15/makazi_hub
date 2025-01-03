# Generated by Django 5.1.3 on 2024-12-04 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('owners', '0010_room_photo_1_room_photo_2_room_photo_3_room_photo_4_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='house',
            name='house_photo_1',
            field=models.ImageField(blank=True, null=True, upload_to='house_photos/', verbose_name='House Photo 1'),
        ),
        migrations.AddField(
            model_name='house',
            name='house_photo_2',
            field=models.ImageField(blank=True, null=True, upload_to='house_photos/', verbose_name='House Photo 2'),
        ),
        migrations.AddField(
            model_name='house',
            name='house_photo_3',
            field=models.ImageField(blank=True, null=True, upload_to='house_photos/', verbose_name='House Photo 3'),
        ),
        migrations.AddField(
            model_name='house',
            name='house_photo_4',
            field=models.ImageField(blank=True, null=True, upload_to='house_photos/', verbose_name='House Photo 4'),
        ),
        migrations.AddField(
            model_name='house',
            name='house_photo_5',
            field=models.ImageField(blank=True, null=True, upload_to='house_photos/', verbose_name='House Photo 5'),
        ),
        migrations.AddField(
            model_name='house',
            name='house_video',
            field=models.FileField(blank=True, null=True, upload_to='house_videos/', verbose_name='House Video'),
        ),
    ]
