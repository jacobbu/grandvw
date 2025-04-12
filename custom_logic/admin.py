from django.contrib import admin
from .models import EventDefinition, GraphDefinition, UserEventAssignment, UserGraphAssignment, CustomChart, SMSRecipient
from .models import CustomMetricCard

admin.site.register(EventDefinition)
admin.site.register(GraphDefinition)
admin.site.register(UserEventAssignment)
admin.site.register(UserGraphAssignment)


@admin.register(CustomChart)
class CustomChartAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'chart_type')
    search_fields = ('name', 'user__username')

@admin.register(CustomMetricCard)
class CustomMetricCardAdmin(admin.ModelAdmin):
    list_display = ["user", "title", "event_type", "period"]
    list_filter = ["user", "event_type", "period"]

class SMSRecipientAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'user', 'event_types')
    search_fields = ('phone_number', 'user__username')

admin.site.register(SMSRecipient, SMSRecipientAdmin)