from rest_framework import serializers
from .models import InsuranceCompany, InsurancePeriod, InsuranceProduct


class InsuranceCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceCompany
        fields = ['id', 'name', 'logo']

from rest_framework import serializers
from .models import InsuranceProduct

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


# serializers.py
from rest_framework import serializers
from .models import AssetInsurance, InsuranceClaim

class AssetInsuranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetInsurance
        fields = '__all__'
        read_only_fields = ['created_by', 'updated_by']


class InsuranceClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceClaim
        fields = '__all__'
        read_only_fields = ['created_bycreated_by', 'updated_by']

