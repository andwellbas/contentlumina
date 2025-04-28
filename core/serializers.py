from rest_framework import serializers
from .models import Prompt, GeneratedContent

class PromptSerializer(serializers.ModelSerializer):
    """
    Serializer for Prompt model (user request)
    """
    class Meta:
        model = Prompt
        fields = ['id', 'text', 'created_at']

class GeneratedContentSerializer(serializers.ModelSerializer):
    """
    Serializer for GeneratedContent model (AI response)
    """
    prompt = PromptSerializer(read_only=True)

    class Meta:
        model = GeneratedContent
        fields = ['id', 'prompt', 'ai_response', 'created_at']