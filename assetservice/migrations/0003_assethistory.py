# Generated by Django 5.1.7 on 2025-04-30 05:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assetservice', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('changed_at', models.DateTimeField(auto_now_add=True)),
                ('weight_kg', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('vaccination_status', models.CharField(blank=True, max_length=20, null=True)),
                ('deworming_status', models.CharField(blank=True, max_length=20, null=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history_records', to='assetservice.asset')),
                ('changed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='asset_change_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-changed_at'],
            },
        ),
    ]
