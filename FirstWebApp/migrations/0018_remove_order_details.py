# Generated by Django 2.2 on 2020-04-27 21:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FirstWebApp', '0017_order_details'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='details',
        ),
    ]