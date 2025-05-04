from decimal import Decimal
from rest_framework import serializers
from .models import Asset, AssetHistory, AssetType


class AssetHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetHistory
        fields = '__all__'


class AssetTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetType
        fields = '__all__'


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = '__all__'
        read_only_fields = ['created_by', 'updated_by', 'created_at', 'updated_at', 'owner']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Convert Decimals to floats for better JSON compatibility
        for key, value in data.items():
            if isinstance(value, Decimal):
                data[key] = float(value)
        return data

    def validate(self, attrs):
        if attrs.get('vaccination_status') == Asset.VaccinationStatus.VACCINATED and not attrs.get('last_vaccination_date'):
            raise serializers.ValidationError("Vaccination date must be provided if the asset is vaccinated.")

        if attrs.get('deworming_status') == Asset.DewormingStatus.DEWORMED and not attrs.get('last_deworming_date'):
            raise serializers.ValidationError("Deworming date must be provided if the asset is dewormed.")

        return attrs

    def create(self, validated_data):
        user = self.context['request'].user

        # Remove protected fields if provided in data
        validated_data.pop('created_by', None)
        validated_data.pop('updated_by', None)
        validated_data.pop('owner', None)

        validated_data['created_by'] = user
        validated_data['updated_by'] = user
        validated_data['owner'] = user

        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context['request'].user

        # Track changes to log in AssetHistory
        changed_fields = {}
        if 'weight_kg' in validated_data and validated_data['weight_kg'] != instance.weight_kg:
            changed_fields['weight_kg'] = validated_data['weight_kg']
        if 'vaccination_status' in validated_data and validated_data['vaccination_status'] != instance.vaccination_status:
            changed_fields['vaccination_status'] = validated_data['vaccination_status']
        if 'deworming_status' in validated_data and validated_data['deworming_status'] != instance.deworming_status:
            changed_fields['deworming_status'] = validated_data['deworming_status']

        # Log changes to AssetHistory if any tracked fields changed
        if changed_fields:
            AssetHistory.objects.create(
                asset=instance,
                changed_by=user,
                weight_kg=changed_fields.get('weight_kg', instance.weight_kg),
                vaccination_status=changed_fields.get('vaccination_status', instance.vaccination_status),
                deworming_status=changed_fields.get('deworming_status', instance.deworming_status),
                remarks="Manual asset update"
            )

        validated_data['updated_by'] = user
        return super().update(instance, validated_data)
