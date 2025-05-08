from django.conf import settings
from django.db import models


def asset_upload_path(instance, filename):
    """Dynamically generate the upload path for asset media."""
    return f'assets/{instance.id}/{filename}'


class AssetType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Breed(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class VaccinationStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class DewormingStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name



class Asset(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_assets")
    asset_type = models.ForeignKey(AssetType, on_delete=models.SET_NULL, null=True, related_name="assets")
    breed = models.ForeignKey(Breed, on_delete=models.SET_NULL, null=True, related_name="assets")
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, related_name="assets")
    age_in_months = models.PositiveIntegerField(help_text="Age in months")
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, help_text="Weight in kilograms")
    vaccination_status = models.ForeignKey(VaccinationStatus, on_delete=models.SET_NULL, null=True, related_name="assets")
    last_vaccination_date = models.DateField(blank=True, null=True)
    deworming_status = models.ForeignKey(DewormingStatus, on_delete=models.SET_NULL, null=True, related_name="assets")
    last_deworming_date = models.DateField(blank=True, null=True)
    special_mark = models.TextField()
    health_issues = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="asset_created")
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="asset_updated")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True, null=True)
    refernce_id = models.TextField(unique=True)

    # Media
    muzzle_video = models.FileField(upload_to=asset_upload_path)
    left_side_image = models.ImageField(upload_to=asset_upload_path)
    right_side_image = models.ImageField(upload_to=asset_upload_path)
    challan_paper = models.FileField(upload_to=asset_upload_path)
    vet_certificate = models.FileField(upload_to=asset_upload_path)
    chairman_certificate = models.FileField(upload_to=asset_upload_path)


    class Meta:
            ordering = ['-created_at']

    def __str__(self):
        return f"{self.asset_type.name if self.asset_type else 'Unknown Type'} - {self.owner.mobile_number}"

    def get_media(self, media_type=None):
        """Retrieve media files associated with the asset, filtered by type."""
        if media_type:
            return self.media_files.filter(media_type__name=media_type)
        return self.media_files.all()


class AssetHistory(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="history_records")
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="asset_change_logs")
    changed_at = models.DateTimeField(auto_now_add=True)
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    vaccination_status = models.ForeignKey(VaccinationStatus, on_delete=models.SET_NULL, null=True, blank=True, related_name="history_vaccinations")
    deworming_status = models.ForeignKey(DewormingStatus, on_delete=models.SET_NULL, null=True, blank=True, related_name="history_dewormings")
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"Asset ID {self.asset.id} - Change by {self.changed_by.mobile_number if self.changed_by else 'Unknown'}"
