from django.urls import path
from .views import *

app_name = 'core'
urlpatterns = [
    path('register/step1/', RegisterStep1.as_view(), name='register-step1'),
    path('register/verify-otp/', VerifyOTP.as_view(), name='verify-otp'),
    path('register/set-password/', SetPassword.as_view(), name='set-password'),
    path('login/', Login.as_view(), name='login'),
    path('personal-info/', SetPersonalInfo.as_view(), name='personal-info'),
    path('financial-info/', SetFinancialInfo.as_view(), name='financial-info'),
    path('nominee-info/', SetNomineeInfo.as_view(), name='nominee-info'),
    path('organization-info/', SetOrganizationInfo.as_view(), name='organization-info'),
    path('token/verify/', VerifyTokenView.as_view(), name='verify-token'),

    path('roles/', RoleListCreateAPIView.as_view(), name='role-list-create'),
    path('roles/<int:pk>/', RoleRetrieveUpdateDestroyAPIView.as_view(), name='role-detail'),

    path('users/sub-users/', SubUsersAPIView.as_view(), name='sub-users'),
]
