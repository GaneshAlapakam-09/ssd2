# Generated by Django 5.1.5 on 2025-05-28 05:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ssdapp', '0008_remove_quotedetails_custom_product_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cash_Book_Master',
            fields=[
                ('S_No', models.IntegerField()),
                ('Expenses_Id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('Date_Time', models.DateTimeField(auto_now=True)),
                ('Date', models.DateField(auto_now=True)),
                ('Cash_In', models.FloatField(default=1500.0)),
                ('Cash_Out', models.FloatField(default=0)),
                ('Balance', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Expense_Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Category', models.CharField(max_length=50, null=True)),
                ('Expense_Name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Cash_Book_Details',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Date', models.DateTimeField(auto_now=True)),
                ('Expenses', models.CharField(max_length=50)),
                ('Expenses_Category', models.CharField(max_length=50)),
                ('Out_Mode', models.CharField(max_length=50, null=True)),
                ('Amount', models.FloatField(null=True)),
                ('Note', models.CharField(max_length=50)),
                ('Expenses_Id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ssdapp.cash_book_master')),
            ],
        ),
    ]
