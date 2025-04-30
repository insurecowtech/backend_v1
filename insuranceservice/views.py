from .serializers import AssetInsuranceSerializer, InsuranceClaimSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import InsuranceCompany, InsuranceType, InsurancePeriod, PremiumPercentage

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
        serializer = AssetInsuranceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InsuranceClaimCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = InsuranceClaimSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_bycreated_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)