# Generated by Django 5.1.3 on 2024-12-25 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('owners', '0025_house_allows_installment_payment_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='house',
            name='is_trending',
            field=models.BooleanField(default=False, verbose_name='Is Trending?'),
        ),
    ]
