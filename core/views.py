from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from .serializers import GeneratedContentSerializer
from .models import Prompt, GeneratedContent
from .services.openai_service import generate_text





class RegisterView(APIView):
    """
    View for register new users.
    Get username, email and password by POST request.
    Create a new user in database
    """

    def post(self, request):
        # Get data from request
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        # Check for required fields
        if not username or not password:
            return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check unique username
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)

        #Create new User
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        return Response({'message': 'User registered successfully!'}, status=status.HTTP_201_CREATED)


class GenerateContentView(APIView):
    """
    View for generate content by OpenAI.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        prompt_text = request.data.get('text')

        if not prompt_text:
            return Response({'error': 'Prompt text is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate request by OpenAI
        ai_response = generate_text(prompt_text)

        # Create Prompt and GeneratedContent in db
        prompt = Prompt.objects.create(user=user, text=prompt_text)
        generated_content = GeneratedContent.objects.create(prompt=prompt, ai_response=ai_response)

        serializer = GeneratedContentSerializer(generated_content)

        return Response(serializer.data, status=status.HTTP_201_CREATED)