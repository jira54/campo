from django.contrib import admin
from .models import Promotion

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'vendor', 'channel', 'segment', 'status', 'created_at')
    list_filter = ('status', 'channel', 'segment', 'created_at')
    search_fields = ('title', 'message', 'vendor__business_name')
    readonly_fields = ('created_at', 'sent_at')
