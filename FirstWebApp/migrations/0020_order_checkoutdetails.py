# Generated by Django 2.2 on 2020-04-30 21:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FirstWebApp', '0019_checkoutdetail_items'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='checkoutdetails',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='FirstWebApp.CheckoutDetail'),
        ),
    ]
