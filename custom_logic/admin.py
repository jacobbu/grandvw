from django.contrib import admin
from .models import EventDefinition, GraphDefinition, UserEventAssignment, UserGraphAssignment, CustomChart
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