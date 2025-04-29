from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from .serializers import GeneratedContentSerializer
from .models import Prompt, GeneratedContent
from .services.openai_service import generate_text
from django.utils import timezone

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required


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

        # Maximum users generations per one day
        max_generations_per_day = 5

        # Check if user not staff or superuser
        if not (user.is_staff or user.is_superuser):
            today = timezone.now().date()
            generation_count = GeneratedContent.objects.filter(
                prompt__user=user,
                created_at__date=today
            ).count()

            if generation_count >= max_generations_per_day:
                return Response(
                    {"error": "Daily generation limit reached. Try again tomorrow."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

        # Generate response by OpenAI
        ai_response = generate_text(prompt_text)

        # Create Prompt and GeneratedContent in db
        prompt = Prompt.objects.create(user=user, text=prompt_text)
        generated_content = GeneratedContent.objects.create(prompt=prompt, ai_response=ai_response)

        serializer = GeneratedContentSerializer(generated_content)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


def register_page(request):
    """
    View for register new user.

    If method POST:
    Get username, email and password from forms.
    If username and password and username unique then Create a new User.
    After register redirect on login page.

    If method GET:
    Show register form.
    """
    if request.method == "POST":
        # Get data from form
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if username and password:
            # Check unique username
            if not User.objects.filter(username=username).exists():
                # Create new user
                User.objects.create_user(username=username, email=email, password=password)
                return redirect('login-page')

    return render(request, 'core/register.html')


def login_page(request):
    """
    View for user login by form.

    If method POST:
    Get username and password.
    Checks if the user exists and the password is correct.
    If yes, login and redirect on generation page.

    If method GET:
    Show login form.
    """
    if request.method == "POST":
        # Get data from form
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('generate-page')

    return render(request, 'core/login.html')


@login_required
def generate_page(request):
    """
    View for generate content by OpenAI on Front.
    Generate text, save prompt and response in db.
    """
    ai_response = None

    if request.method == "POST":
        prompt_text = request.POST.get("text")
        if prompt_text:
            # Generate response by OpenAI
            ai_response = generate_text(prompt_text)

            # Save prompt in db
            prompt = Prompt.objects.create(user=request.user, text=prompt_text)

            # Save response AI in db
            GeneratedContent.objects.create(prompt=prompt, ai_response=ai_response)

    return render(request, 'core/generate.html', {"ai_response": ai_response})