import random

from django.contrib.auth import authenticate
from django.db import IntegrityError, DatabaseError
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from .models import TempUser, User, Role, OTPCategory, OTPRequestLog, OTPVerification, Token, UserPersonalInfo, \
    UserFinancialInfo, UserNomineeInfo, OrganizationInfo
from django.utils.timezone import now
from datetime import timedelta, datetime


def validate_mobile_number(value):
    if User.objects.filter(mobile_number=value).exists():
        raise serializers.ValidationError("User already exists.")
    elif TempUser.objects.filter(mobile_number=value, is_verified=True).exists():
        raise serializers.ValidationError("User already exists.")
    return value

class LoginSerializer(serializers.Serializer):
    mobile_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        mobile_number = attrs.get('mobile_number')
        password = attrs.get('password')

        user = authenticate(mobile_number=mobile_number, password=password)
        if not user:
            raise AuthenticationFailed("Invalid mobile number or password")

        if not user.is_active:
            raise AuthenticationFailed("This account is disabled.")

        # Get or create token for user
        token_obj, _ = Token.objects.get_or_create(user=user)
        token_obj.generate_tokens()  # Will only regenerate if missing or invalid

        return {
            'role': user.role.name if user.role else None,
            'access_token': token_obj.access_token,
            'refresh_token': token_obj.refresh_token,
        }

class Step1Serializer(serializers.Serializer):
    mobile_number = serializers.CharField()
    role_id = serializers.IntegerField()
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)

    def create(self, validated_data):
        request = self.context.get('request')
        mobile_number = validated_data['mobile_number']
        role_id = validated_data['role_id']
        latitude = validated_data['latitude']
        longitude = validated_data['longitude']

        category = OTPCategory.REGISTRATION

        # Validate mobile number
        try:
            validate_mobile_number(mobile_number)
        except Exception as e:
            raise serializers.ValidationError({"detail": f"Invalid mobile number: {str(e)}"})

        # Check OTP request limit
        if OTPRequestLog.request_limit_exceeded(mobile_number, category):
            raise serializers.ValidationError({"detail": "OTP request limit exceeded. Please try again later."})

        otp_code = str(random.randint(100000, 999999))

        # Update or create TempUser
        try:
            temp_user, created = TempUser.objects.update_or_create(
                mobile_number=mobile_number,
                defaults={
                    'role_id': role_id,
                    'otp': otp_code,
                    'is_verified': False,
                    'latitude': latitude,
                    'longitude': longitude,
                }
            )

            # Update OTP request count
            if created or (temp_user.updated_at < now() - timedelta(hours=24)):
                temp_user.otp_request_count = 1
            else:
                temp_user.otp_request_count += 1
            temp_user.save()

            # Save OTP and log request
            ip = request.META.get('REMOTE_ADDR', 'Unknown IP')
            ua = request.META.get('HTTP_USER_AGENT', 'Unknown User Agent')

            otp_instance = OTPRequestLog.objects.create(
                mobile_number=mobile_number,
                otp_code=otp_code,
                category=category,
                ip_address=ip,
                user_agent=ua
            )

            OTPVerification.objects.create(
                otp=otp_instance,
                is_verified=False
            )

            # Replace print with proper logging or SMS sending
            print(f"OTP sent: {otp_code}")
            return temp_user

        except IntegrityError as e:
            raise serializers.ValidationError({"detail": f"Database integrity error: {str(e)}"})
        except DatabaseError as e:
            raise serializers.ValidationError({"detail": f"Database error: {str(e)}"})
        except Exception as e:
            raise serializers.ValidationError({"detail": f"Unexpected error: {str(e)}"})


class OTPVerifySerializer(serializers.Serializer):
    mobile_number = serializers.CharField()
    otp = serializers.CharField()

    def validate(self, attrs):
        try:
            temp_user = TempUser.objects.get(mobile_number=attrs['mobile_number'], otp=attrs['otp'])
            attrs['temp_user'] = temp_user
        except TempUser.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP or mobile number.")
        return attrs

    def save(self):
        temp_user = self.validated_data['temp_user']
        temp_user.is_verified = True
        temp_user.save()

        otp_instance = OTPRequestLog.objects.filter(
            mobile_number=temp_user.mobile_number,
        ).order_by('-created_at').first()

        if not otp_instance:
            raise serializers.ValidationError("OTP request not found.")

        otp_instance2 = OTPVerification.objects.get(
            otp=otp_instance,
            is_verified=False
        )

        if not otp_instance2:
            raise serializers.ValidationError("OTP verification entry not found or already verified.")

        otp_instance2.is_verified = True
        otp_instance2.verified_at = timezone.now()
        otp_instance2.save()

        return temp_user

class SetPasswordSerializer(serializers.Serializer):
    mobile_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            temp_user = TempUser.objects.get(mobile_number=attrs['mobile_number'], is_verified=True)
            attrs['temp_user'] = temp_user
        except TempUser.DoesNotExist:
            raise serializers.ValidationError("OTP not verified or user not found.")
        return attrs

    def create(self, validated_data):
        temp_user = validated_data['temp_user']
        # Check if user already exists before trying to authenticate
        existing_user = User.objects.filter(mobile_number=temp_user.mobile_number).first()
        if existing_user:
            raise serializers.ValidationError("User already exists. Please login instead.")

        user = User.objects.create_user(
            mobile_number=temp_user.mobile_number,
            password=validated_data['password'],
            role=temp_user.role
        )
        return user


class SetPersonalInfoSerializer(serializers.ModelSerializer):
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = UserPersonalInfo
        fields = [
            'profile_image',
            'profile_image_url',
            'first_name',
            'last_name',
            'nid',
            'date_of_birth',
            'gender',
            'tin',
            'nid_front',
            'nid_back'
        ]
        extra_kwargs = {
            'profile_image': {'write_only': True}  # Only accept uploads, but don't show in GET
        }

    def get_profile_image_url(self, obj):
        request = self.context.get('request')
        if request and obj.profile_image and hasattr(obj.profile_image, 'url'):
            return request.build_absolute_uri(obj.profile_image.url)
        return None

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.is_active:
            raise serializers.ValidationError("User is not active.")

        # Check if the user already has personal info
        personal_info = UserPersonalInfo.objects.filter(user=user).first()
        if personal_info and personal_info.update_count >= 1:
            raise serializers.ValidationError("You can update your personal information only once.")

        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data.pop('user')

        try:
            # Update or create the personal info for the user
            user_info, created = UserPersonalInfo.objects.update_or_create(
                user=user, defaults=validated_data
            )

            # Increment update_count only if updating an existing record
            if not created:
                user_info.update_count += 1
                user_info.save()
                print("Existing UserPersonalInfo updated.")
            else:
                print("New UserPersonalInfo created.")

            return user_info

        except IntegrityError as e:
            raise serializers.ValidationError(f"Database error occurred: {str(e)}")
        except Exception as e:
            raise serializers.ValidationError(f"Unexpected error occurred: {str(e)}")


from rest_framework import serializers
from django.db import IntegrityError


class SetOrganizationInfoSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = OrganizationInfo
        fields = [
            'logo',
            'logo_url',
            'name',
            'established',
            'tin',
            'bin'
        ]
        extra_kwargs = {
            'logo': {'write_only': True}  # Only accept uploads, but don't show in GET
        }

    def get_logo_url(self, obj):
        request = self.context.get('request')
        if obj.logo and hasattr(obj.logo, 'url'):
            return request.build_absolute_uri(obj.logo.url)
        return None

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.is_active:
            raise serializers.ValidationError("User is not active.")

        # Check user role for authorization
        if user.role_id not in (2, 3):
            raise serializers.ValidationError("User is not authorized.")

        # Check if the organization info has been updated once already
        org_info = OrganizationInfo.objects.filter(user=user).first()
        if org_info and org_info.update_count >= 1:
            raise serializers.ValidationError("You can update your organization information only once.")

        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data.pop('user')

        try:
            # Update or create the organization info for the user
            org_info, created = OrganizationInfo.objects.update_or_create(
                user=user,
                defaults=validated_data
            )

            # Increment update_count if updating an existing record
            if not created:
                org_info.update_count += 1
                org_info.save()
                print("Existing OrganizationInfo updated.")
            else:
                print("New OrganizationInfo created.")

            return org_info

        except IntegrityError as e:
            raise serializers.ValidationError(f"Database error occurred: {str(e)}")
        except Exception as e:
            raise serializers.ValidationError(f"Unexpected error occurred: {str(e)}")


class SetFinancialInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFinancialInfo
        fields =  [ "bank_name", "branch_name","account_name","account_number"]
    def validate(self, attrs):
        user = self.context['request'].user
        if not user.is_active:
            raise serializers.ValidationError("User is not active.")

        # Check if financial info already exists and update limit exceeded
        financial_info = UserFinancialInfo.objects.filter(user=user).first()
        if financial_info and financial_info.update_count >= 1:
            raise serializers.ValidationError("You can update your financial information only once.")

        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data.pop('user')

        # Update or create the financial info for the user
        financial_info, created = UserFinancialInfo.objects.update_or_create(
            user=user,
            defaults=validated_data
        )

        # Increment update_count if updating an existing record
        if not created:
            financial_info.update_count += 1
            financial_info.save()
            print("Existing Financial Info updated.")
        else:
            print("New Financial Info created.")

        return financial_info

class SetNomineeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNomineeInfo
        fields =  [ "nominee_name", "phone","email","nid"]

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.is_active:
            raise serializers.ValidationError("User is not active.")

        # Check if financial info already exists and update limit exceeded
        nominee_info = UserNomineeInfo.objects.filter(user=user).first()
        if nominee_info and nominee_info.update_count >= 1:
            raise serializers.ValidationError("You can update your nominee information only once.")

        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data.pop('user')

        # Update or create the financial info for the user
        nominee_info, created = UserNomineeInfo.objects.update_or_create(
            user=user,
            defaults=validated_data
        )

        # Increment update_count if updating an existing record
        if not created:
            nominee_info.update_count += 1
            nominee_info.save()
            print("Existing Nominee Info updated.")
        else:
            print("New Nominee Info created.")

        return nominee_info


from rest_framework import serializers
from .models import (
    User, UserPersonalInfo, UserFinancialInfo, UserNomineeInfo,
    OrganizationInfo, InsuranceCompany
)
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name',]

class UserPersonalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPersonalInfo
        fields = '__all__'
        read_only_fields = ['user']


class UserFinancialInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFinancialInfo
        fields = '__all__'
        read_only_fields = ['user']


class UserNomineeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNomineeInfo
        fields = '__all__'
        read_only_fields = ['user']


class OrganizationInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationInfo
        fields = '__all__'
        read_only_fields = ['user']


class InsuranceCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceCompany
        fields = '__all__'
        read_only_fields = ['user']

from rest_framework import serializers
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    personal_info = UserPersonalInfoSerializer(required=False)
    financial_info = UserFinancialInfoSerializer(required=False)
    nominee_info = UserNomineeInfoSerializer(required=False)
    organization_info = OrganizationInfoSerializer(required=False)

    class Meta:
        model = User
        fields = [
            'id', 'mobile_number', 'password', 'role', 'managed_by', 'onboarded_by',
            'personal_info', 'financial_info', 'nominee_info', 'organization_info',
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': True}  # Secure password handling
        }

    def validate_password(self, value):
        if not value:
            raise serializers.ValidationError("Password cannot be blank.")
        return value

    def validate_managed_by(self, value):
        request_user = self.context['request'].user
        if value:
            if not request_user.is_superuser:
                raise serializers.ValidationError("Only superusers can assign managed_by.")
            if value.role_id != 2:
                raise serializers.ValidationError("managed_by must be a user with role_id = 2.")
        return value

    def validate_onboarded_by(self, value):
        if value and not (value.is_staff or value.is_superuser):
            raise serializers.ValidationError("Onboarded_by must be a staff or superuser.")
        return value

    def create(self, validated_data):
        # Extract nested data
        personal_info_data = validated_data.pop('personal_info', None)
        financial_info_data = validated_data.pop('financial_info', None)
        nominee_info_data = validated_data.pop('nominee_info', None)
        organization_info_data = validated_data.pop('organization_info', None)
        password = validated_data.get('password', None)

        if not password:
            raise serializers.ValidationError({"password": ["This field cannot be blank..........."]})

        # Create the user without nested data
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        # Create related objects after user creation

        # Personal Info
        if personal_info_data:
            personal_info, created = UserPersonalInfo.objects.update_or_create(
                user=user,
                defaults=personal_info_data
            )
            user.personal_info = personal_info
            user.save()

        # Financial Info
        if financial_info_data:
            financial_info, created = UserFinancialInfo.objects.update_or_create(
                user=user,
                defaults=financial_info_data
            )
            user.financial_info = financial_info
            user.save()

        # Nominee Info
        if nominee_info_data:
            nominee_info, created = UserNomineeInfo.objects.update_or_create(
                user=user,
                defaults=nominee_info_data
            )
            user.nominee_info = nominee_info
            user.save()

        # Organization Info (for roles 2 or 3 only)
        if organization_info_data and user.role_id in (2, 3):
            org_info, created = OrganizationInfo.objects.update_or_create(
                user=user,
                defaults=organization_info_data
            )
            user.organization_info = org_info
            user.save()

        return user


class SubUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'mobile_number', 'role', 'is_active', 'date_joined']


from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New password and confirmation do not match.")

        try:
            validate_password(data['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": e.messages})

        return data
