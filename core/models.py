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


class MovieRecommendation(models.Model):
    """
        A model for storing movie recommendations generated based on a user query.

        Attributes:
            user (ForeignKey): A link to the user who sent the request.
            prompt (TextField): Incoming user request or preference (e.g. genres, countries, etc.).
            response (TextField): The system's response with movie recommendations.
            created_at (DateTimeField): Date and time the recommendation was created.

        Methods:
            __str__: Returns a string representation of an object in the format "Recommendation for <username> at <date>".
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prompt = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recommendation for {self.user.username} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class SeriesRecommendation(models.Model):
    """
        A model for storing series recommendations generated based on a user query.

        Attributes:
            user (ForeignKey): A link to the user who sent the request.
            prompt (TextField): Incoming user request or preference (e.g. genres, countries, etc.).
            response (TextField): The system's response with movie recommendations.
            created_at (DateTimeField): Date and time the recommendation was created.

        Methods:
            __str__: Returns a string representation of an object in the format "Recommendation for <username> at <date>".
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prompt = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recommendation for {self.user.username} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"