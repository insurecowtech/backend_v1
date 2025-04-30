from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('authservice.urls'), name='auth-api'),
    path('api/v1/insurance/', include('insuranceservice.urls'), name='insurance-api'),
    path('api/v1/asset/', include('assetservice.urls'), name='assetservice-api'),
    path('api/v1/administrator/', include('administrator.urls'), name='administrator-api'),
]
