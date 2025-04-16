from django.contrib import admin
from .models import EventDefinition, GraphDefinition, UserEventAssignment, UserGraphAssignment, CustomChart, SMSRecipient
from .models import CustomMetricCard, DetectionLabel, ModelPerformanceImage
from django.utils.html import format_html

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

@admin.register(DetectionLabel)
class DetectionLabelAdmin(admin.ModelAdmin):
    list_display = ("label", "user", "image_preview")
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image_with_box:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.image_with_box.url)
        return "(no image)"

@admin.register(ModelPerformanceImage)
class ModelPerformanceImageAdmin(admin.ModelAdmin):
    list_display = ("user", "description", "image_preview")
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.image.url)
        return "(no image)"

class SMSRecipientAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'user', 'event_types')
    search_fields = ('phone_number', 'user__username')

admin.site.register(SMSRecipient, SMSRecipientAdmin)