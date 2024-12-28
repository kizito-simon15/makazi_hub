# Generated by Django 5.1.3 on 2024-12-27 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('owners', '0030_house_is_new'),
    ]

    operations = [
        migrations.AddField(
            model_name='house',
            name='is_pet_friendly',
            field=models.BooleanField(default=False, verbose_name='Is the house pet friendly?'),
        ),
    ]
