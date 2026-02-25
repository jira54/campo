from django.db import models
from django.conf import settings
from django.utils import timezone


class Note(models.Model):
    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} — {self.vendor.business_name}"

    @property
    def excerpt(self):
        """Return first 100 characters of content."""
        return self.content[:100] + '...' if len(self.content) > 100 else self.content

    @property
    def is_recent(self):
        """Return True if updated in last 24 hours."""
        return (timezone.now() - self.updated_at).total_seconds() < 86400
