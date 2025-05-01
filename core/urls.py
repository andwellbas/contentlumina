from django.urls import path
from . import views


urlpatterns = [
    # Front
    path("register/", views.register_page, name="register-page"), # Register
    path("login/", views.login_page, name="login-page"), # Login
    path("generate/", views.generate_page, name="generate-page"), # Generate
    path("", views.home_page, name="home"),
    path("movies/", views.movie_recommender, name="movie-recommender"),
]
