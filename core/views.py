from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from .serializers import GeneratedContentSerializer
from .models import Prompt, GeneratedContent, MovieRecommendation, SeriesRecommendation
from .services.openai_service import generate_text, generate_movie_recommendations
from django.utils import timezone

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

import requests
from django.conf import settings


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

        return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)


class GenerateContentView(APIView):
    """
    View for generate content by OpenAI.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        prompt_text = request.data.get("text")

        if not prompt_text:
            return Response({"error": "Prompt text is required."}, status=status.HTTP_400_BAD_REQUEST)

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

        # reCAPTCHA verification
        captcha_response = request.POST.get("g-recaptcha-response")
        verify_url = "https://www.google.com/recaptcha/api/siteverify"
        payload = {
            "secret": settings.RECAPTCHA_SECRET_KEY,
            "response": captcha_response
        }
        res = requests.post(verify_url, data=payload)
        result = res.json()

        if not result.get("success"):
            return render(request, "core/register.html", {
                "error": "reCAPTCHA verification failed",
                "RECAPTCHA_SITE_KEY": settings.RECAPTCHA_SITE_KEY
            })


        # Checking that all fields are filled in
        if not username or not email or not password:
            return render(request, "core/register.html", {
                "error": "All fields are required.."
            })

        # Checking uniqueness
        if User.objects.filter(username=username).exists():
            return render(request, "core/register.html", {
                "error": "This username is already taken"
            })
        elif User.objects.filter(email=email).exists():
            return render(request, "core/register.html", {
                "error": "This email is already registered"
            })

        # Everything ok, create a user
        User.objects.create_user(username=username, email=email, password=password)
        return redirect("login-page")

    return render(request, "core/register.html", {"RECAPTCHA_SITE_KEY": settings.RECAPTCHA_SITE_KEY})


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

        # reCAPTCHA verification
        captcha_response = request.POST.get("g-recaptcha-response")
        verify_url = "https://www.google.com/recaptcha/api/siteverify"
        payload = {
            "secret": settings.RECAPTCHA_SECRET_KEY,
            "response": captcha_response
        }
        res = requests.post(verify_url, data=payload)
        result = res.json()

        if not result.get("success"):
            return render(request, "core/login.html", {
                "error": "reCAPTCHA verification failed",
                "RECAPTCHA_SITE_KEY": settings.RECAPTCHA_SITE_KEY
            })

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            return render(request, "core/login.html", {"error": "Incorrect login or password"})

    return render(request, "core/login.html", {"RECAPTCHA_SITE_KEY": settings.RECAPTCHA_SITE_KEY})


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

    return render(request, "core/generate.html", {"ai_response": ai_response})


def home_page(request):
    """
    Simple home page.
    """
    return render(request, "core/home.html")


@login_required
def movie_recommender(request):
    """
    View for generating movie recommendations via OpenAI.
    Gets data from the form, builds a prompt, calls generate_movie_recommendations(),
    returns a response to the user.
    """
    context = {}

    if request.method == "POST":
        # Getting data from a form
        genre1 = request.POST.get("genre1")
        genre2 = request.POST.get("genre2")
        year_from = request.POST.get("year_from")
        year_to = request.POST.get("year_to")
        country = request.POST.get("country")
        fav1 = request.POST.get("fav1")
        fav2 = request.POST.get("fav2")
        fav3 = request.POST.get("fav3")
        wishlist = request.POST.get("wishlist")

        # Building a prompt
        user_prompt_parts = []

        if genre1:
            user_prompt_parts.append(f"Genre: {genre1}")
        if genre2:
            user_prompt_parts.append(f"Second genre: {genre2}")
        if year_from or year_to:
            user_prompt_parts.append(f"Year of release: from {year_from or 'any'} to {year_to or 'today'}")
        if country:
            user_prompt_parts.append(f"Country of manufacture: {country}")
        favs = [f for f in [fav1, fav2, fav3] if f]
        if favs:
            user_prompt_parts.append(f"I like these kinds of movies: {', '.join(favs)}")
        if wishlist:
            user_prompt_parts.append(f"Now I want to watch something like this: {wishlist}")

        user_prompt = "\n".join(user_prompt_parts)

        # Full prompt for GPT
        gpt_prompt = (
                "Recommend 3 movies in the format:\n"
                "Movie title\nYear: XXXX\nGenres: genre1, genre2, ...\nDescription: ...\n"
                "Use only existing films in English.\n\n" +
                user_prompt
        )

        # Calling GPT via an openai_service.py
        gpt_response = generate_movie_recommendations(gpt_prompt)

        context["prompt"] = user_prompt
        context["result"] = gpt_response
        context["submitted"] = True

        # Save prompt and response to db
        MovieRecommendation.objects.create(
            user=request.user,
            prompt=user_prompt,
            response=gpt_response
        )


    return render(request, "core/movie_recommender.html", context)


@login_required
def series_recommender(request):
    """
    View for generating TV series recommendations via OpenAI.
    Gets data from the form, builds a prompt, calls generate_movie_recommendations(),
    returns a response to the user.
    """
    context = {}

    if request.method == "POST":
        # Getting data from a form
        genre1 = request.POST.get("genre1")
        genre2 = request.POST.get("genre2")
        year_from = request.POST.get("year_from")
        year_to = request.POST.get("year_to")
        country = request.POST.get("country")
        fav1 = request.POST.get("fav1")
        fav2 = request.POST.get("fav2")
        fav3 = request.POST.get("fav3")
        wishlist = request.POST.get("wishlist")

        # Building a prompt
        user_prompt_parts = []

        if genre1:
            user_prompt_parts.append(f"Genre: {genre1}")
        if genre2:
            user_prompt_parts.append(f"Second genre: {genre2}")
        if year_from or year_to:
            user_prompt_parts.append(f"Year of release: from {year_from or 'any'} to {year_to or 'today'}")
        if country:
            user_prompt_parts.append(f"Country of manufacture: {country}")
        favs = [f for f in [fav1, fav2, fav3] if f]
        if favs:
            user_prompt_parts.append(f"I like these kinds of series: {', '.join(favs)}")
        if wishlist:
            user_prompt_parts.append(f"Now I want to watch something like this: {wishlist}")

        user_prompt = "\n".join(user_prompt_parts)

        # Full prompt for GPT
        gpt_prompt = (
            "Recommend 3 TV series in the format:\n"
            "Title\nYear: XXXX\nGenres: genre1, genre2, ...\nDescription: 1-2 sentence summary.\n"
            "Use only existing real series in English.\n\n" +
            user_prompt
        )

        # Calling GPT via openai_service.py
        gpt_response = generate_movie_recommendations(gpt_prompt)

        context["prompt"] = user_prompt
        context["result"] = gpt_response
        context["submitted"] = True

        # Save prompt and response to db
        SeriesRecommendation.objects.create(
            user=request.user,
            prompt=user_prompt,
            response=gpt_response
        )

    return render(request, "core/series_recommender.html", context)


@login_required
def movies_history(request):
    """
    View to display the user's movies recommendation history.
    """
    user = request.user
    recommendations = MovieRecommendation.objects.filter(user=user).order_by("-created_at")
    return render(request, "core/history.html", {"recommendations": recommendations})


@login_required
def series_history(request):
    """
    View to display the user's series recommendation history.
    """
    user = request.user
    recommendations = SeriesRecommendation.objects.filter(user=user).order_by("-created_at")
    return render(request, "core/series_history.html", {"recommendations": recommendations})