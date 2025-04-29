from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Role)
admin.site.register(User)
admin.site.register(TempUser)
admin.site.register(OTPLimit)
admin.site.register(OTPRequestLog)
admin.site.register(OTPVerification)
admin.site.register(UserLocation)
admin.site.register(UserPersonalInfo)
admin.site.register(UserFinancialInfo)
admin.site.register(UserNomineeInfo)
admin.site.register(OrganizationInfo)
admin.site.register(Token)
