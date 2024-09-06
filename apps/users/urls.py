from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path('request-code/', views.RequestCodeView.as_view(), name='request-code'),
    path("verify-code/", views.CodeVerificationView.as_view(), name='verify-code'),
    path("sign-up/", views.SignUpView.as_view(), name='sign-up'),
    path("active-user/", views.ActiveUserView.as_view(), name='active-user'),
]