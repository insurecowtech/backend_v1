# Generated by Django 5.1.7 on 2025-05-07 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authservice', '0006_userpersonalinfo_update_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizationinfo',
            name='update_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
