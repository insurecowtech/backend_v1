from django.contrib import admin

from assetservice.models import AssetType, Asset

# Register your models here.
admin.site.register(AssetType)
admin.site.register(Asset)
