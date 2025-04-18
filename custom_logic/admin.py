from django.contrib import admin
from .models import EventDefinition, GraphDefinition, UserEventAssignment, UserGraphAssignment, CustomChart, SMSRecipient
from .models import CustomMetricCard, DetectionLabel, ModelPerformanceImage, DailySummary, UserKnowledgeBase, DailySummarySubscription
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
    list_filter = ('user',)
    fields = ('user', 'phone_number', 'event_types', 'message_template')

admin.site.register(SMSRecipient, SMSRecipientAdmin)

@admin.register(DailySummary)
class DailySummaryAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'short_summary', 'created_at', 'generated_by')
    list_filter = ('date', 'user', 'generated_by')
    search_fields = ('user__username', 'summary_text')
    readonly_fields = ('created_at',)

    def short_summary(self, obj):
        return (obj.summary_text[:75] + '...') if len(obj.summary_text) > 75 else obj.summary_text
    short_summary.short_description = 'Summary Preview'

@admin.register(UserKnowledgeBase)
class UserKnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ("user", "updated_at")
    search_fields = ("user__username",)

@admin.register(DailySummarySubscription)
class DailySummarySubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user']