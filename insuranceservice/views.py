from Insurecow.utils import success_response, handle_serializer_error, validation_error_from_serializer
from .serializers import AssetInsuranceSerializer, InsuranceClaimSerializer
from rest_framework.response import Response
from rest_framework import status, serializers
from .models import InsuranceCompany, InsuranceType, InsurancePeriod, PremiumPercentage, InsuranceCategory


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import InsuranceCategory, InsuranceType, InsurancePeriod, PremiumPercentage
from .serializers import InsuranceCategorySerializer, InsuranceTypeSerializer, InsurancePeriodSerializer, PremiumPercentageSerializer

from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

class InsuranceCategoryListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_superuser:
            categories = InsuranceCategory.objects.all()
        elif request.user.role.id == 3:
            categories = InsuranceCategory.objects.filter(company=request.user.insurance_company)
        else:
            raise PermissionDenied("You are not authorized to view these insurance categories.")

        serializer = InsuranceCategorySerializer(categories, many=True)
        return success_response("Insurance categories retrieved successfully.", data=serializer.data)

    def post(self, request):
        if not request.user.is_superuser and request.user.role.id != 3:
            raise PermissionDenied("You are not authorized to create insurance categories.")

        serializer = InsuranceCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response("Insurance category created successfully.", data=serializer.data)
        return validation_error_from_serializer(serializer)

class InsuranceCategoryDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        category = get_object_or_404(InsuranceCategory, pk=pk)
        serializer = InsuranceCategorySerializer(category)
        return success_response("Insurance category retrieved successfully.", data=serializer.data)

    def put(self, request, pk):
        category = get_object_or_404(InsuranceCategory, pk=pk)
        serializer = InsuranceCategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response("Insurance category updated successfully.", data=serializer.data)
        return validation_error_from_serializer(serializer)

    def delete(self, request, pk):
        category = get_object_or_404(InsuranceCategory, pk=pk)
        category.delete()
        return success_response("Insurance category deleted successfully.")


class PremiumPercentageListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        percentages = PremiumPercentage.objects.all()
        serializer = PremiumPercentageSerializer(percentages, many=True)
        return success_response("Premium percentages retrieved successfully.", data=serializer.data)

    def post(self, request):
        serializer = PremiumPercentageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response("Premium percentage created successfully.", data=serializer.data)
        return validation_error_from_serializer(serializer)


class PremiumPercentageDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        percentage = get_object_or_404(PremiumPercentage, pk=pk)
        serializer = PremiumPercentageSerializer(percentage)
        return success_response("Premium percentage retrieved successfully.", data=serializer.data)

    def put(self, request, pk):
        percentage = get_object_or_404(PremiumPercentage, pk=pk)
        serializer = PremiumPercentageSerializer(percentage, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response("Premium percentage updated successfully.", data=serializer.data)
        return validation_error_from_serializer(serializer)

    def delete(self, request, pk):
        percentage = get_object_or_404(PremiumPercentage, pk=pk)
        percentage.delete()
        return success_response("Premium percentage deleted successfully.")



class CompanyWiseInsuranceAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        companies = InsuranceCompany.objects.all()
        data = []

        for company in companies:
            company_data = {
                "id": company.id,
                "name": company.name,
                "logo": request.build_absolute_uri(company.logo.url) if company.logo else None,
                "insurance_types": [],
            }

            insurance_types = InsuranceType.objects.filter(company=company)

            for insurance_type in insurance_types:
                type_data = {
                    "id": insurance_type.id,
                    "name": insurance_type.name,
                    "periods": []
                }

                insurance_periods = InsurancePeriod.objects.filter(
                    company=company,
                    category=insurance_type.category
                )

                for period in insurance_periods:
                    premiums = PremiumPercentage.objects.filter(
                        company=company,
                        category=insurance_type.category,
                        insurance_type=insurance_type,
                        insurance_period=period
                    )

                    premium_list = []
                    for premium in premiums:
                        premium_list.append({
                            "id": premium.id,
                            "percentage": premium.percentage
                        })

                    type_data["periods"].append({
                        "id": period.id,
                        "name": period.name,
                        "premiums": premium_list
                    })

                company_data["insurance_types"].append(type_data)

            data.append(company_data)

        return Response({
            "statusCode": str(status.HTTP_200_OK),
            "statusMessage": "Success",
            "data": data
        }, status=status.HTTP_200_OK)


class AssetInsuranceCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        is_many = isinstance(request.data, list)
        serializer = AssetInsuranceSerializer(data=request.data, many=is_many, context={'request': request})

        if serializer.is_valid():
            try:
                serializer.save(created_by=request.user)
                return success_response(
                    "Asset Insurance(s) created successfully.",data=serializer.data,
                    status_code=status.HTTP_201_CREATED
                )
            except serializers.ValidationError as e:
                return handle_serializer_error(e)

        return validation_error_from_serializer(serializer)


class InsuranceClaimCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = InsuranceClaimSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(created_bycreated_by=request.user)
                return success_response("Asset Insurance Claimed successfully.",data=serializer.data, status_code=status.HTTP_201_CREATED)

            except serializers.ValidationError as e:
                return handle_serializer_error(e)

        return validation_error_from_serializer(serializer)