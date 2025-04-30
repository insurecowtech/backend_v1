from django.conf import settings
from django.db import models


def asset_upload_path(instance, filename):
    return f'asset/{instance.pk}/{filename}'

class AssetType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Asset(models.Model):
    class VaccinationStatus(models.TextChoices):
        VACCINATED = 'vaccinated', 'Vaccinated'
        NOT_VACCINATED = 'not_vaccinated', 'Not Vaccinated'

    class DewormingStatus(models.TextChoices):
        DEWORMED = 'dewormed', 'Dewormed'
        NOT_DEWORMED = 'not_dewormed', 'Not Dewormed'

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_assets")
    asset_type = models.ForeignKey(AssetType, on_delete=models.SET_NULL, null=True, related_name="assets")
    breed = models.CharField(max_length=255, blank=True, null=True)
    age_in_months = models.PositiveIntegerField(help_text="Age in months")
    color = models.CharField(max_length=255)
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, help_text="Weight in kilograms")

    vaccination_status = models.CharField(max_length=20, choices=VaccinationStatus.choices)
    last_vaccination_date = models.DateField(blank=True, null=True)
    deworming_status = models.CharField(max_length=20, choices=DewormingStatus.choices)
    last_deworming_date = models.DateField(blank=True, null=True)

    special_mark = models.TextField(blank=True, null=True)
    health_issues = models.TextField(blank=True, null=True)

    # Media
    muzzle_video = models.FileField(upload_to=asset_upload_path, blank=True, null=True)
    left_side_image = models.ImageField(upload_to=asset_upload_path, blank=True, null=True)
    right_side_image = models.ImageField(upload_to=asset_upload_path, blank=True, null=True)
    challan_paper = models.FileField(upload_to=asset_upload_path, blank=True, null=True)
    vet_certificate = models.FileField(upload_to=asset_upload_path, blank=True, null=True)
    chairman_certificate = models.FileField(upload_to=asset_upload_path, blank=True, null=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asset_created"
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asset_updated"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.asset_type.name if self.asset_type else 'Unknown Type'} - {self.owner.name}"

class AssetHistory(models.Model):
    asset = models.ForeignKey("Asset", on_delete=models.CASCADE, related_name="history_records")

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asset_change_logs"
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    vaccination_status = models.CharField(max_length=20, blank=True, null=True)
    deworming_status = models.CharField(max_length=20, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)  # Optional comments on the change

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"Change for Asset ID {self.asset.id} at {self.changed_at}"
