# Generated by Django 5.1.5 on 2025-05-06 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ssdapp', '0006_remove_employee_blood_group_remove_employee_pan'),
    ]

    operations = [
        migrations.AddField(
            model_name='billingdetails',
            name='Additional_Charges',
            field=models.FloatField(null=True),
        ),
    ]
