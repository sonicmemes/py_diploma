# Generated by Django 5.1.1 on 2024-10-16 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shop',
            name='state',
            field=models.BooleanField(choices=[('on', 'On'), ('off', 'Off')], max_length=3, verbose_name='статус получения заказов'),
        ),
    ]
