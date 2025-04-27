from django.contrib import admin
from .models import Prompt, GeneratedContent


@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")
    search_fields = ("user__username", "text")


@admin.register(GeneratedContent)
class GeneratedContentAdmin(admin.ModelAdmin):
    list_display = ("id", "prompt", "created_at")
    search_fields = ("prompt__text", "ai_response")

