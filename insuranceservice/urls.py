from django.urls import path
from .views import *

app_name = 'insurance_portal'
urlpatterns = [
    path('insurance-product/', CompanyWiseInsuranceAPIView.as_view(), name='nominee-info'),
    path('insurance-apply/', AssetInsuranceCreateAPIView.as_view(), name='asset-insurance-apply'),
    path('insurance-claim/', InsuranceClaimCreateAPIView.as_view(), name='insurance-claim'),

]
