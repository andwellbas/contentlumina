from django.db import models
from django.contrib.auth.models import User


class Prompt(models.Model):
    """
    Model for saving users requests to AI
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="prompts")
    text = models.TextField(help_text="User request text")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prompt {self.id} by {self.user.username}"


class GeneratedContent(models.Model):
    """
    Model for save response from AI by users requests
    """

    prompt = models.OneToOneField(Prompt, on_delete=models.CASCADE, related_name="generated_content")
    ai_response = models.TextField(help_text="AI response")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"GeneratedContent for Prompt {self.prompt.id}"
