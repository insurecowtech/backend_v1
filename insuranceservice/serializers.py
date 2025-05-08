from rest_framework import serializers
from .models import InsuranceCompany, InsurancePeriod, InsuranceProduct, InsuranceCategory, InsuranceType, \
    PremiumPercentage, AssetInsurance, InsuranceClaim


class InsuranceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceCategory
        fields = '__all__'


class InsuranceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceType
        fields = '__all__'


class InsurancePeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsurancePeriod
        fields = '__all__'


class PremiumPercentageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PremiumPercentage
        fields = '__all__'


class InsuranceProductSerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField()
    insurance_type = serializers.SerializerMethodField()
    insurance_period = serializers.SerializerMethodField()

    class Meta:
        model = InsuranceProduct
        fields = [
            "id",
            "company",
            "insurance_type",
            "insurance_period",
            "premium_percentage",
            "description",
        ]

    def get_company(self, obj):
        return {
            "id": obj.company.id,
            "value": obj.company.name
        }

    def get_insurance_type(self, obj):
        return {
            "id": obj.insurance_type.id,
            "value": obj.insurance_type.name
        }

    def get_insurance_period(self, obj):
        return {
            "id": obj.insurance_period.id,
            "value": obj.insurance_period.name
        }


class AssetInsuranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetInsurance
        fields = '__all__'
        extra_kwargs = {
            'created_by': {'read_only': True},
        }

    def create(self, validated_data):
        created_by = self.context['request'].user
        if isinstance(validated_data, list):
            for item in validated_data:
                item['created_by'] = created_by
            return AssetInsurance.objects.bulk_create([
                AssetInsurance(**item) for item in validated_data
            ])
        validated_data['created_by'] = created_by
        return super().create(validated_data)



class InsuranceClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceClaim
        fields = '__all__'
        read_only_fields = ['created_bycreated_by', 'updated_by']

