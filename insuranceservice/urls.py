from django.urls import path
from .views import *

app_name = 'insurance_portal'
urlpatterns = [
    # path('insurance-categories/', InsuranceCategoryListCreateAPIView.as_view(), name='insurance-category-list'),
    # path('insurance-categories/<int:pk>/', InsuranceCategoryDetailAPIView.as_view(), name='insurance-category-detail'),

    # # Insurance Type URLs
    # path('insurance-types/', InsuranceTypeAPIView.as_view(), name='insurance-type-list'),
    # path('insurance-types/<int:pk>/', InsuranceTypeDetailAPIView.as_view(), name='insurance-type-detail'),
    #
    # # Insurance Period URLs
    # path('insurance-periods/', InsurancePeriodAPIView.as_view(), name='insurance-period-list'),
    # path('insurance-periods/<int:pk>/', InsurancePeriodDetailAPIView.as_view(), name='insurance-period-detail'),
    #
    # # Premium Percentage URLs
    # path('premium-percentages/', PremiumPercentageListCreateAPIView.as_view(), name='premium-percentage-list'),
    # path('premium-percentages/<int:pk>/', PremiumPercentageDetailAPIView.as_view(), name='premium-percentage-detail'),


    path('insurance-product/', CompanyWiseInsuranceAPIView.as_view(), name='nominee-info'),
    path('insurance-apply/', AssetInsuranceCreateAPIView.as_view(), name='asset-insurance-apply'),
    path('insurance-claim/', InsuranceClaimCreateAPIView.as_view(), name='insurance-claim'),

]
