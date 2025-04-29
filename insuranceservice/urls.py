from django.urls import path
from .views import *

app_name = 'insurance_portal'
urlpatterns = [
    path('insurance-product/', CompanyWiseInsuranceAPIView.as_view(), name='nominee-info'),
]
