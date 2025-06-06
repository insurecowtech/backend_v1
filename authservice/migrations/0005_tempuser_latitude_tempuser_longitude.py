# Generated by Django 5.1.7 on 2025-05-07 03:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authservice', '0004_userpersonalinfo_nid_back_userpersonalinfo_nid_front'),
    ]

    operations = [
        migrations.AddField(
            model_name='tempuser',
            name='latitude',
            field=models.DecimalField(decimal_places=6, default=1, max_digits=9),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tempuser',
            name='longitude',
            field=models.DecimalField(decimal_places=6, default=1, max_digits=9),
            preserve_default=False,
        ),
    ]
