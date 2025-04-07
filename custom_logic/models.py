from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class EventDefinition(models.Model):
    name = models.CharField(max_length=255)
    import_path = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class GraphDefinition(models.Model):
    name = models.CharField(max_length=255)
    import_path = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class UserEventAssignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event_def = models.ForeignKey(EventDefinition, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} → {self.event_def}"

class UserGraphAssignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    graph_def = models.ForeignKey(GraphDefinition, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} → {self.graph_def}"

