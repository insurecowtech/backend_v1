import random

from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from .models import TempUser, User, Role, OTPCategory, OTPRequestLog, OTPVerification, Token, UserPersonalInfo, \
    UserFinancialInfo, UserNomineeInfo, OrganizationInfo
from django.utils.timezone import now
from datetime import timedelta

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

    def create(self, validated_data):
        request = self.context.get('request')
        mobile_number = validated_data['mobile_number']
        role_id = validated_data['role_id']
        category = OTPCategory.REGISTRATION
        validate_mobile_number(mobile_number)
        validate_mobile_number(mobile_number)
        # Check OTP request limit
        if OTPRequestLog.request_limit_exceeded(mobile_number, category):
            raise serializers.ValidationError({"detail": "OTP request limit exceeded. Please try again later."})

        otp_code = str(random.randint(100000, 999999))

        # Update or create TempUser
        temp_user, created = TempUser.objects.update_or_create(
            mobile_number=mobile_number,
            defaults={
                'role_id': role_id,
                'otp': otp_code,
                'is_verified': False
            }
        )

        # Reset count if older than 24 hours
        if temp_user.updated_at < now() - timedelta(hours=24):
            temp_user.otp_request_count = 1
        else:
            temp_user.otp_request_count += 1
        temp_user.save()

        # Save OTP
        ip = request.META.get('REMOTE_ADDR')
        ua = request.META.get('HTTP_USER_AGENT')

        # Save log
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
        print(f"OTP sent: {otp_code}")  # Replace with SMS sending
        return temp_user

from django.core.exceptions import MultipleObjectsReturned

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

        otp_instance2 = OTPVerification.objects.filter(
            otp=otp_instance,
            is_verified=False
        ).order_by('-created_at').first()

        if not otp_instance2:
            raise serializers.ValidationError("OTP verification entry not found or already verified.")

        otp_instance2.is_verified = True
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
            'tin'
        ]
        extra_kwargs = {
            'profile_image': {'write_only': True}  # Only accept uploads, but don't show in GET
        }

    def get_profile_image_url(self, obj):
        request = self.context.get('request')
        if obj.profile_image and hasattr(obj.profile_image, 'url'):
            return request.build_absolute_uri(obj.profile_image.url)
        return None

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.is_active:
            raise serializers.ValidationError("User is not active.")
        if hasattr(user, 'personal_info'):
            raise serializers.ValidationError("Personal info already exists for this user.")
        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data.pop('user')
        return UserPersonalInfo.objects.update_or_create(user=user, **validated_data)

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
        if user.role_id not in (2,3):
            raise serializers.ValidationError("User is not authorized.")
        if hasattr(user,
                   'organization_info') and user.organization_info.logo and user.organization_info.name != '':
            raise serializers.ValidationError("Organization info already exists for this user with a logo.")

        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        OrganizationInfo.objects.update_or_create(
            user=user,
            defaults={
                "name": validated_data["name"],
                "established": validated_data.get("established"),
                "tin": validated_data.get("tin"),
                "bin": validated_data.get("bin"),
                "logo": validated_data.get("logo"),
            }
        )
        return user


class SetFinancialInfoSerializer(serializers.Serializer):
    bank_name = serializers.CharField(required=True)
    branch_name = serializers.CharField(required=True)
    account_name = serializers.CharField(required=True)
    account_number = serializers.CharField(required=True)

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.is_active:
            raise serializers.ValidationError("User is not active.")
        if hasattr(user, 'financial_info'):
            raise serializers.ValidationError("Financial info already exists for this user.")
        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data.pop('user')
        UserFinancialInfo.objects.update_or_create(user=user, **validated_data)
        return user

class SetNomineeInfoSerializer(serializers.Serializer):
    nominee_name = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    nid = serializers.CharField(required=True)

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.is_active:
            raise serializers.ValidationError("User is not active.")
        if hasattr(user, 'nominee_info'):
            raise serializers.ValidationError("Financial info already exists for this user.")
        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data.pop('user')
        UserNomineeInfo.objects.update_or_create(user=user, **validated_data)
        return user
