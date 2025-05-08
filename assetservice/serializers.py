from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import (
    Asset, AssetHistory, AssetType, Breed, Color, VaccinationStatus,
    DewormingStatus
)


User = get_user_model()


class AssetTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetType
        fields = ['id', 'name']


class BreedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Breed
        fields = ['id', 'name', 'description']


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name', 'description']


class VaccinationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaccinationStatus
        fields = ['id', 'name', 'description']


class DewormingStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DewormingStatus
        fields = ['id', 'name', 'description']

class AssetHistorySerializer(serializers.ModelSerializer):
    changed_by = serializers.StringRelatedField()

    class Meta:
        model = AssetHistory
        fields = '__all__'

from rest_framework import serializers
from .models import Asset, AssetType, Breed, Color, VaccinationStatus, DewormingStatus
from django.contrib.auth import get_user_model


class AssetSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all(), required=False)
    asset_type = serializers.PrimaryKeyRelatedField(queryset=AssetType.objects.all(), required=True)
    breed = serializers.PrimaryKeyRelatedField(queryset=Breed.objects.all(), required=True)
    color = serializers.PrimaryKeyRelatedField(queryset=Color.objects.all(), required=True)
    vaccination_status = serializers.PrimaryKeyRelatedField(queryset=VaccinationStatus.objects.all(), required=True)
    deworming_status = serializers.PrimaryKeyRelatedField(queryset=DewormingStatus.objects.all(), required=True)
    muzzle_video = serializers.FileField(required=True)
    left_side_image = serializers.ImageField(required=True)
    right_side_image = serializers.ImageField(required=True)
    challan_paper = serializers.FileField(required=True)
    vet_certificate = serializers.FileField(required=True)
    chairman_certificate = serializers.FileField(required=True)

    class Meta:
        model = Asset
        fields = '__all__'
        read_only_fields = ['created_by', 'updated_by', 'created_at', 'updated_at']

    def validate(self, attrs):
        user = self.context['request'].user

        # Check if all mandatory fields are present
        mandatory_fields = ['asset_type', 'breed', 'color', 'vaccination_status', 'deworming_status']
        for field in mandatory_fields:
            if field not in attrs or not attrs[field]:
                raise serializers.ValidationError({field: f"{field.replace('_', ' ').capitalize()} is mandatory."})


        if user.is_superuser:
            # If the user is not an owner (role.id != 1), the 'owner' must be explicitly passed in the request body
            if 'owner' not in attrs or not attrs['owner']:
                raise serializers.ValidationError({"owner": "Owner must be provided for users who are not owners."})

            # Optionally, you can add extra validation to ensure the passed owner is a valid user
            if attrs['owner'] == user:
                raise serializers.ValidationError({"owner": "You cannot assign the asset to yourself."})
        elif user.role.id == 1:
            # If the user is an owner (role.id == 1), automatically set owner to the current user
            attrs['owner'] = user
        else:
            # If the user is not an owner (role.id != 1), the 'owner' must be explicitly passed in the request body
            if 'owner' not in attrs or not attrs['owner']:
                raise serializers.ValidationError({"owner": "Owner must be provided for users who are not owners."})

            # Optionally, you can add extra validation to ensure the passed owner is a valid user
            if attrs['owner'] == user:
                raise serializers.ValidationError({"owner": "You cannot assign the asset to yourself."})

        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['created_by'] = user
        validated_data['updated_by'] = user

        # Create the asset
        asset = super().create(validated_data)

        return asset

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.updated_by = user

        # Perform ownership validation during update as well
        if user.role.id == 1:
            if 'owner' in validated_data and validated_data['owner'] != user:
                raise serializers.ValidationError({"owner": "You cannot change the owner to another user."})
            validated_data['owner'] = user
        else:
            if 'owner' not in validated_data or not validated_data['owner']:
                raise serializers.ValidationError({"owner": "Owner must be provided for this role."})

        # Define fields that are allowed to be updated
        updatable_fields = [
            'age_in_months', 'weight_kg',
            'vaccination_status', 'last_vaccination_date', 'deworming_status',
            'last_deworming_date', 'special_mark', 'health_issues', 'is_active',
            'remarks', 'muzzle_video', 'left_side_image',
            'right_side_image', 'challan_paper', 'vet_certificate',
            'chairman_certificate'
        ]

        # Iterate through the validated data and update only the allowed fields
        for field in updatable_fields:
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        # Save the updated instance
        instance.save()

        return instance


