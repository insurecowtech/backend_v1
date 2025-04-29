from .serializers import AssetInsuranceSerializer, InsuranceClaimSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import InsuranceCompany, InsuranceType, InsurancePeriod, PremiumPercentage

# class CreateInsuranceCompany(APIView):
#     permission_classes = [IsAuthenticated]
#     def post(self, request):
#         serializer = InsuranceCompanySerializer(data=request.data, context={'request': request})
#         if serializer.is_valid():
#             try:
#                 serializer.save()
#                 return success_response("Insurance Company created successfully.")
#
#             except serializers.ValidationError as e:
#                 return handle_serializer_error(e)
#
#         return validation_error_from_serializer(serializer)
# class CreateScopeOfcover(APIView):
#     permission_classes = [IsAuthenticatedOrReadOnly]
#
#     def post(self, request):
#         serializer = ScopeOfcoverSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({'message': 'Scope of Cover created successfully.', 'data': serializer.data}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class CreateInsurancePeriod(APIView):
#     permission_classes = [IsAuthenticatedOrReadOnly]
#
#     def post(self, request):
#         serializer = InsurancePeriodSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({'message': 'Insurance Period created successfully.', 'data': serializer.data}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CompanyWiseInsuranceAPIView(APIView):
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