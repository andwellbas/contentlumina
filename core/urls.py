from django.urls import path
from . import views

from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView


urlpatterns = [
    # Front
    path("register/", views.register_page, name="register-page"), # Register
    path("login/", views.login_page, name="login-page"), # Login
    path("profile/", views.profile_view, name="profile"), # User Profile
    path("verify-register-code/", views.verify_register_code, name="verify-register-code"), # Email confirm
    path("logout/", LogoutView.as_view(next_page="home"), name="logout"), # Logaut
    path("generate/", views.generate_page, name="generate-page"), # Generate

    path("", views.home_page, name="home"), # Home Page
    path("movies/", views.movie_recommender, name="movie-recommender"), # Movies recommend page
    path("series/", views.series_recommender, name="series-recommender"), # Series recommend page
    path("login-required/", TemplateView.as_view(
        template_name="core/login_required.html"), name="login-required"), # Login Check
]
