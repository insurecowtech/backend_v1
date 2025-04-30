from django.urls import path
from .views import *

app_name = 'assetservice'

urlpatterns = [
    path('assets/', AssetListAPIView.as_view(), name='asset-list'),
    path('assets/create/', AssetCreateAPIView.as_view(), name='asset-create'),
    path('assets/<int:pk>/', AssetDetailAPIView.as_view(), name='asset-detail'),
    path('assets/create-on-behalf/', AssetCreateOnBehalfAPIView.as_view(), name='create_asset_on_behalf'),
]

