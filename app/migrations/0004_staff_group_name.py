# Generated by Django 3.2.7 on 2021-10-30 18:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20211030_1801'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='group_name',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.companyschedulename'),
        ),
    ]
