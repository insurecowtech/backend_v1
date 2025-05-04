from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('authservice.urls'), name='auth-api'),
    path('api/v1/insurance/', include('insuranceservice.urls'), name='insurance-api'),
    path('api/v1/asset/', include('assetservice.urls'), name='assetservice-api'),
    path('api/v1/administrator/', include('administrator.urls'), name='administrator-api'),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT})

]
