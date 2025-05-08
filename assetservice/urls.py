from django.urls import path
from .views import *

app_name = 'assetservice'

urlpatterns = [

    path('assets-type/', AssetTypeListAPIView.as_view(), name='asset-type-list'),
    path('admin/assets-type/', AssetTypeCreateAPIView.as_view(), name='asset-type-create'),
    path('admin/assets-type/<int:pk>/', AssetTypeDetailAPIView.as_view(), name='asset-type-detail'),


    path('breeds/', BreedListAPIView.as_view(), name='breed-list'),
    path('admin/breeds/', BreedCreateAPIView.as_view(), name='breed-create'),
    path('admin/breeds/<int:pk>/', BreedDetailAPIView.as_view(), name='breed-detail'),

    path('colors/', ColorListAPIView.as_view(), name='color-list'),
    path('admin/colors/', ColorCreateAPIView.as_view(), name='color-create'),
    path('admin/colors/<int:pk>/', ColorDetailAPIView.as_view(), name='color-detail'),

    path('vaccination-status/', VaccinationStatusListAPIView.as_view(), name='vaccination-status-list'),
    path('admin/vaccination-status/', VaccinationStatusCreateAPIView.as_view(), name='vaccination-status-create'),
    path('admin/vaccination-status/<int:pk>/', VaccinationStatusDetailAPIView.as_view(), name='vaccination-status-detail'),

    path('deworming-status/', DewormingStatusListAPIView.as_view(), name='deworming-status-list'),
    path('admin/deworming-status/', DewormingStatusCreateAPIView.as_view(), name='deworming-status-create'),
    path('admin/deworming-status/<int:pk>/', DewormingStatusDetailAPIView.as_view(), name='deworming-status-detail'),




    path('asset-list/', AssetListAPIView.as_view(), name='asset-list'),
    path('create-asset/', AssetCreateAPIView.as_view(), name='asset-create'),
    path('assets/<int:pk>/', AssetDetailAPIView.as_view(), name='asset-detail'),

    # path('assets/create-on-behalf/', AssetCreateOnBehalfAPIView.as_view(), name='create_asset_on_behalf'),


]

