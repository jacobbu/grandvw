from django.contrib import admin
from .models import EventDefinition, GraphDefinition, UserEventAssignment, UserGraphAssignment

admin.site.register(EventDefinition)
admin.site.register(GraphDefinition)
admin.site.register(UserEventAssignment)
admin.site.register(UserGraphAssignment)
