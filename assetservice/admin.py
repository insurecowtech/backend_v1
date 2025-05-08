from django.contrib import admin

from assetservice.models import *

# Register your models here.
admin.site.register(AssetType)
admin.site.register(Asset)
admin.site.register(Breed)
admin.site.register(Color)
admin.site.register(VaccinationStatus)
admin.site.register(DewormingStatus)
admin.site.register(AssetHistory)