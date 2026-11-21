from django.contrib import admin

from .models import DatabaseFile


@admin.register(DatabaseFile)
class DatabaseFileAdmin(admin.ModelAdmin):
    list_display = ("name", "content_type", "size", "updated_at")
    search_fields = ("name",)
    readonly_fields = ("name", "content_type", "size", "created_at", "updated_at")
