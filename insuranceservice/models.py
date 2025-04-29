from datetime import date

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from assetservice.models import Asset

class InsuranceCompany(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="insurance_company")
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='logo/')

    def __str__(self):
        return self.name


class InsuranceCategory(models.Model):
    company = models.ForeignKey(InsuranceCompany, on_delete=models.CASCADE, related_name="insurance_categories")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class InsuranceType(models.Model):
    company = models.ForeignKey(InsuranceCompany, on_delete=models.CASCADE, related_name="insurance_types")
    category = models.ForeignKey(InsuranceCategory, on_delete=models.CASCADE, related_name="insurance_types")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class InsurancePeriod(models.Model):
    company = models.ForeignKey(InsuranceCompany, on_delete=models.CASCADE, related_name="insurance_periods")
    category = models.ForeignKey(InsuranceCategory, on_delete=models.CASCADE, related_name="insurance_periods")
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class PremiumPercentage(models.Model):
    company = models.ForeignKey(InsuranceCompany, on_delete=models.CASCADE, related_name="premium_percentages")
    category = models.ForeignKey(InsuranceCategory, on_delete=models.CASCADE, related_name="premium_percentages")
    insurance_type = models.ForeignKey(InsuranceType, on_delete=models.CASCADE, related_name="premium_percentages")
    insurance_period = models.ForeignKey(InsurancePeriod, on_delete=models.CASCADE, related_name="premium_percentages")
    percentage = models.FloatField(help_text="Premium as percentage of asset value annually")

    def __str__(self):
        return f"{self.insurance_type.name} - {self.percentage}% per {self.insurance_period.name}"


class InsuranceProduct(models.Model):
    company = models.ForeignKey(InsuranceCompany, on_delete=models.CASCADE, related_name="insurance_products")
    category = models.ForeignKey(InsuranceCategory, on_delete=models.CASCADE, related_name="insurance_products")
    insurance_type = models.ForeignKey(InsuranceType, on_delete=models.CASCADE, related_name="insurance_products")
    insurance_period = models.ForeignKey(InsurancePeriod, on_delete=models.CASCADE, related_name="insurance_products")
    premium_percentage = models.FloatField(help_text="Premium as a percentage of asset value annually")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.company.name} | {self.insurance_type.name} | {self.insurance_period.name} ({self.premium_percentage}%)"


class AssetInsurance(models.Model):
    class InsuranceStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        EXPIRED = 'expired', 'Expired'
        CANCELLED = 'cancelled', 'Cancelled'

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="insurances")
    insurance_provider = models.ForeignKey(InsuranceCompany, on_delete=models.SET_NULL, null=True, blank=True)
    insurance_number = models.CharField(max_length=100, unique=True)
    sum_insured = models.DecimalField(max_digits=10, decimal_places=2)
    premium_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    insurance_start_date = models.DateField()
    insurance_end_date = models.DateField()
    insurance_status = models.CharField(max_length=20, choices=InsuranceStatus.choices, default=InsuranceStatus.ACTIVE)

    policy_terms = models.TextField(blank=True, null=True)
    insurance_certificate = models.FileField(upload_to='asset/insurance_certificates/', blank=True, null=True)
    insurance_agent = models.CharField(max_length=255, blank=True, null=True)

    renewal_reminder_sent = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asset_insurance_created"
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asset_insurance_updated"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    remarks = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Insurance {self.insurance_number} for Asset ID {self.asset.id}"

    @property
    def is_currently_active(self):
        today = date.today()
        return self.insurance_start_date <= today <= self.insurance_end_date and self.insurance_status == self.InsuranceStatus.ACTIVE

    @property
    def days_until_expiry(self):
        if self.insurance_end_date:
            return (self.insurance_end_date - date.today()).days
        return None

class InsuranceClaim(models.Model):
    class ClaimStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        UNDER_REVIEW = 'under_review', 'Under Review'

    asset_insurance = models.ForeignKey(AssetInsurance, on_delete=models.CASCADE, related_name="claims")
    claim_date = models.DateField(auto_now_add=True)
    reason = models.TextField()
    amount_claimed = models.DecimalField(max_digits=10, decimal_places=2)
    amount_approved = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    claim_status = models.CharField(max_length=20, choices=ClaimStatus.choices, default=ClaimStatus.PENDING)

    claim_documents = models.FileField(upload_to='asset/claim_documents/', blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    processed_date = models.DateField(blank=True, null=True)
    settlement_documents = models.FileField(upload_to='asset/settlement_documents/', blank=True, null=True)

    created_bycreated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="insurance_created"
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="insurance_updated"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    remarks = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Claim {self.id} for Insurance {self.asset_insurance.insurance_number}"


@receiver(post_save, sender=PremiumPercentage)
def create_or_update_insurance_product(sender, instance, created, **kwargs):
    try:
        # Fetch or create an InsuranceProduct based on company, insurance_type and insurance_period
        insurance_product, product_created = InsuranceProduct.objects.get_or_create(
            company=instance.company,
            category=instance.category,
            insurance_type=instance.insurance_type,
            insurance_period=instance.insurance_period,
            defaults={
                'premium_percentage': instance.percentage,
                'description': instance.insurance_type.description
            }
        )

        if not product_created:
            # If existing, update premium and description
            insurance_product.premium_percentage = instance.percentage
            insurance_product.description = instance.insurance_type.description
            insurance_product.save()

        action = "created" if product_created else "updated"
        print(f"Insurance Product {action} for {instance.company.name}")

    except Exception as e:
        print(f"Error while creating/updating InsuranceProduct: {str(e)}")
