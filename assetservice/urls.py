from django.urls import path
from .views import *

app_name = 'assetservice'

urlpatterns = [

    path('assets-type/', AssetTypeListAPIView.as_view(), name='asset-type-list'),
    path('assets-type/<int:pk>/', AssetTypeDetailAPIView.as_view(), name='asset-type-detail'),

    path('assets/', AssetListAPIView.as_view(), name='asset-list'),
    path('assets/<int:pk>/', AssetDetailAPIView.as_view(), name='asset-detail'),
    path('assets/create/', AssetCreateAPIView.as_view(), name='asset-create'),
    path('assets/<int:pk>/', AssetDetailAPIView.as_view(), name='asset-detail'),
    path('assets/create-on-behalf/', AssetCreateOnBehalfAPIView.as_view(), name='create_asset_on_behalf'),


]

