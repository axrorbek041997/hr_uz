# Generated by Django 3.2.9 on 2021-12-16 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_auto_20211216_1730'),
    ]

    operations = [
        migrations.CreateModel(
            name='FreeTrial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('days', models.IntegerField(default=7)),
            ],
        ),
    ]
