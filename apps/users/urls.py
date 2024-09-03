from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'users'
urlpatterns = [
    path('', views.HomePage.as_view(), name='home'),
    path("request-code/", views.RequestCodePage.as_view(), name="request-code"),
    path("verify-code/", views.VerifyCodePage.as_view(), name="verify-code"),
    path("sign-up/", views.SignUpPage.as_view(), name='sign-up'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]