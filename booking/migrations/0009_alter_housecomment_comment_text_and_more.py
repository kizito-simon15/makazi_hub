# Generated by Django 5.1.3 on 2024-12-09 18:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0008_housecomment_delete_roomcomment'),
        ('owners', '0019_remove_bookingrule_payment_method_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='housecomment',
            name='comment_text',
            field=models.TextField(help_text='The text of the comment.', verbose_name='Comment Text'),
        ),
        migrations.AlterField(
            model_name='housecomment',
            name='house',
            field=models.ForeignKey(help_text='The house this comment belongs to.', on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='owners.house', verbose_name='House'),
        ),
    ]
