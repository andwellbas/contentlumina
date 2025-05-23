from django.contrib import admin
from .models import Prompt, GeneratedContent, MovieRecommendation, SeriesRecommendation, AnimeRecommendation, GameRecommendation


@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")
    search_fields = ("user__username", "text")


@admin.register(GeneratedContent)
class GeneratedContentAdmin(admin.ModelAdmin):
    list_display = ("id", "prompt", "created_at")
    search_fields = ("prompt__text", "ai_response")


@admin.register(MovieRecommendation)
class MovieRecommendationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")


@admin.register(SeriesRecommendation)
class SeriesRecommendationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")

@admin.register(AnimeRecommendation)
class AnimeRecommendationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")


@admin.register(GameRecommendation)
class GameRecommendationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")