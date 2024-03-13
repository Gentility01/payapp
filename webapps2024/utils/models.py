import auto_prefetch
from django.db import models

class VisibleManager(auto_prefetch.Manager):
    def get_queryset(self):
        """filters queryset to return only visible items"""
        return super().get_queryset().filter(visible=True)


class TimeBasedModel(auto_prefetch.Model):
    visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(auto_prefetch.Model.Meta):
        abstract = True
        base_manager_name = "prefetch_manager"  # Correction: Added base_manager_name

    objects = auto_prefetch.Manager()
    items = VisibleManager()