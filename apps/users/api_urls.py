from django.urls import path
from . import api_views

app_name = 'users-api'
urlpatterns = [
    path('request-code/', api_views.RequestCodeView.as_view(), name='request-code'),
    path("verify-code/", api_views.CodeVerificationView.as_view(), name='verify-code'),
    path("sign-up/", api_views.SignUpView.as_view(), name='sign-up'),
    path("active-user/", api_views.ActiveUserView.as_view(), name='active-user'),
]