# Generated by Django 3.2.7 on 2021-11-01 11:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20211030_1859'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyschedulename',
            name='company',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.company'),
        ),
    ]