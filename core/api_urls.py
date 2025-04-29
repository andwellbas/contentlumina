from django.urls import path
from .views import RegisterView, GenerateContentView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    # API
    path("register/", RegisterView.as_view(), name="register"), # Registration
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"), # Login and get token
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"), # Refresh access token
    path('generate/', GenerateContentView.as_view(), name='generate-content'), # Generate ai content
]