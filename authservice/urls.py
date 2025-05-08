from django.urls import path
from .views import *

app_name = 'core'
urlpatterns = [
    path('public/register/step1/', RegisterStep1.as_view(), name='register-step1'),
    path('public/register/verify-otp/', VerifyOTP.as_view(), name='verify-otp'),
    path('public/register/set-password/', SetPassword.as_view(), name='set-password'),
    path('public/login/', Login.as_view(), name='login'),

    path('user/personal-info/', SetPersonalInfo.as_view(), name='personal-info'),
    path('user/financial-info/', SetFinancialInfo.as_view(), name='financial-info'),
    path('user/nominee-info/', SetNomineeInfo.as_view(), name='nominee-info'),
    path('user/organization-info/', SetOrganizationInfo.as_view(), name='organization-info'),

    path('public/token/verify/', VerifyTokenView.as_view(), name='verify-token'),

    path('public/role-list/', RoleListAPIView.as_view(), name='role-list'),
    path('admin/role/', RoleListCreateAPIView.as_view(), name='role-list-create'),
    path('admin/role/<int:pk>/', RoleRetrieveUpdateDestroyAPIView.as_view(), name='role-detail'),

    path('user/sub-users/', SubUsersAPIView.as_view(), name='sub-users'),

    path('user/change-password/', ChangePasswordAPIView.as_view(), name='change-password'),
]
