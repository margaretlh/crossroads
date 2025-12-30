from django.contrib import admin
from .models import WhiteLabelConfiguration, WhiteLabelConfigurationAdmin

admin.site.register(WhiteLabelConfiguration, WhiteLabelConfigurationAdmin)
