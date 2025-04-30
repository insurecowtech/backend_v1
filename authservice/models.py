from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import now
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from rest_framework_simplejwt.tokens import RefreshToken

from insuranceservice.models import InsuranceCompany


class TimestampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class Role(TimestampModel):
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class TempUser(TimestampModel):
    mobile_number = models.CharField(max_length=15, unique=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    otp = models.CharField(max_length=6)
    otp_request_count = models.PositiveIntegerField(default=0)
    is_verified = models.BooleanField(default=False)


    def __str__(self):
        return self.mobile_number

    class Meta:
        indexes = [
            models.Index(fields=["mobile_number"]),
        ]

class UserManager(BaseUserManager):
    def create_user(self, mobile_number, password=None, **extra_fields):
        if not mobile_number:
            raise ValueError("Users must have a mobile number")
        user = self.model(mobile_number=mobile_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", None)
        extra_fields.setdefault("managed_by", None)
        extra_fields.setdefault("onboarded_by", None)
        return self.create_user(mobile_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    mobile_number = models.CharField(max_length=15, unique=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    managed_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_users',
        help_text="Must be a user with role_id = 2"
    )

    onboarded_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='onboarded_users',
        help_text="Only staff or superuser can onboard other users"
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)


    objects = UserManager()

    USERNAME_FIELD = "mobile_number"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.mobile_number

    class Meta:
        indexes = [
            models.Index(fields=["mobile_number"]),
        ]

    def clean(self):
        if self.is_superuser:
            return  # Skip validation for superusers

        if self.managed_by and self.managed_by.role_id != 2:
            raise ValidationError("The manager must have role_id = 2.")

        if self.onboarded_by and not (self.onboarded_by.is_staff or self.onboarded_by.is_superuser):
            raise ValidationError("Onboarded_by must be a staff or superuser.")

    def save(self, *args, **kwargs):
        self.full_clean()  # triggers clean()
        super().save(*args, **kwargs)

class OTPCategory(models.TextChoices):
    REGISTRATION = "registration", "Registration"
    PASSWORD_RESET = "password_reset", "Password Reset"
    LOGIN = "login", "Login"

class OTPLimit(TimestampModel):
    category = models.CharField(max_length=20, choices=OTPCategory.choices, unique=True)
    max_attempts = models.PositiveIntegerField(default=5)
    time_window = models.PositiveIntegerField(default=10)

    def __str__(self):
        return f"{self.category} - {self.max_attempts} OTPs in {self.time_window} minutes"

class OTPRequestLog(TimestampModel):
    mobile_number = models.CharField(max_length=15)
    otp_code = models.CharField(max_length=6)
    category = models.CharField(max_length=20, choices=OTPCategory.choices)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.mobile_number} - {self.otp_code} ({self.category}) @ {self.created_at}"


    class Meta:
        indexes = [
            models.Index(fields=["mobile_number", "category"]),
        ]


    @classmethod
    def request_limit_exceeded(cls, mobile_number, category):
        default_max_attempts = 5
        default_time_window = 5  # in minutes

        try:
            otp_limit = OTPLimit.objects.get(category=category)
            max_attempts = otp_limit.max_attempts
            time_window = otp_limit.time_window
        except OTPLimit.DoesNotExist:
            max_attempts = default_max_attempts
            time_window = default_time_window

        time_threshold = now() - timedelta(minutes=time_window)
        recent_requests = cls.objects.filter(
            mobile_number=mobile_number,
            category=category,
            created_at__gte=time_threshold
        ).count()

        return recent_requests >= max_attempts

class OTPVerification(TimestampModel):
    otp = models.ForeignKey(OTPRequestLog, on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"OTP {self.otp.otp_code} verification status: {self.is_verified}"

class LocationCategory(models.TextChoices):
    REGISTRATION = "registration", "Registration"
    PASSWORD_RESET = "password_reset", "Password Reset"
    LOGIN = "login", "Login"

class UserLocation(TimestampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=LocationCategory.choices)
    lat = models.FloatField()
    long = models.FloatField()

    def __str__(self):
        return f"{self.user.mobile_number} - {self.category} Location"


class UserPersonalInfo(TimestampModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="personal_info")
    profile_image = models.ImageField(null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    nid = models.CharField(max_length=50, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)

    tin = models.CharField("TIN", max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user.mobile_number}"

class OrganizationInfo(TimestampModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="organization_info")
    logo = models.ImageField(null=True, blank=True)
    name = models.CharField(max_length=255)
    established = models.DateField(null=True, blank=True)
    tin = models.CharField("TIN", max_length=50, null=True, blank=True)
    bin = models.CharField("BIN", max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user.mobile_number}"

class UserFinancialInfo(TimestampModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="financial_info")
    bank_name = models.CharField(max_length=100)
    branch_name = models.CharField(max_length=100)
    account_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)

    def __str__(self):
        return f"Financial Info for {self.user.mobile_number}"

class UserNomineeInfo(TimestampModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="nominee_info")
    nominee_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(null=True, blank=True)
    nid = models.CharField(max_length=50)

    def __str__(self):
        return f"Nominee Info for {self.user.mobile_number}"

class Token(TimestampModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="token")
    access_token = models.TextField()
    refresh_token = models.TextField()

    def is_token_valid(self):
        try:
            AccessToken(self.access_token)
            return True
        except TokenError:
            return False

    def generate_tokens(self, force=False):
        if force or not self.access_token or not self.refresh_token or not self.is_token_valid():
            refresh = RefreshToken.for_user(self.user)
            self.access_token = str(refresh.access_token)
            self.refresh_token = str(refresh)
            self.save()

    def __str__(self):
        return f"Token for {self.user.mobile_number}"


@receiver(post_save, sender=User)
def create_user_token(sender, instance, created, **kwargs):
    if created:
        token, token_created = Token.objects.get_or_create(user=instance)
        if token_created or not token.access_token or not token.refresh_token or not token.is_token_valid():
            token.generate_tokens()
            print(f"Tokens generated for {instance.mobile_number}")

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Safely create related profiles only if they don't already exist
        if not hasattr(instance, 'personal_info'):
            UserPersonalInfo.objects.create(user=instance)

        if not hasattr(instance, 'financial_info'):
            UserFinancialInfo.objects.create(user=instance)

        if not hasattr(instance, 'nominee_info'):
            UserNomineeInfo.objects.create(user=instance)

        print(f"User profile created for {instance.mobile_number}")

        if instance.role_id in (2, 3):
            if not hasattr(instance, 'organization_info'):
                OrganizationInfo.objects.create(user=instance)
                print(f"Organization profile created for {instance.mobile_number}")

        if instance.role_id == 3:
            if not hasattr(instance, 'insurance_company'):
                InsuranceCompany.objects.create(user=instance)


@receiver(post_save, sender=OrganizationInfo)
def update_insurance_company(sender, instance, created, **kwargs):
    try:
        insurance_company = InsuranceCompany.objects.get(user=instance.user)
        insurance_company.name = instance.name
        insurance_company.logo = instance.logo
        insurance_company.save()
        print(f"Insurance company updated for user {instance.user.mobile_number}")
    except InsuranceCompany.DoesNotExist:
        print(f"No InsuranceCompany found for user {instance.user.mobile_number}")