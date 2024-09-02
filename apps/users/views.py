from django.shortcuts import render, redirect
from django.views import View
from .forms import EmailForm, CodeVerificationForm, SignUpForm
from django.http import JsonResponse, HttpResponse
import requests
from django.urls import reverse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


class HomePage(View):
    def get(self, request):
        auth = JWTAuthentication()
        user = None
        try:
            # Authenticate the request
            result = auth.authenticate(request)
            if result is not None:
                user, _ = result
            else:
                # If authentication returns None
                return redirect('users:request-code')
        except AuthenticationFailed:
            # Handle authentication failure
            return redirect('users:request-code')

        if user is not None:
            # User is authenticated
            return HttpResponse("hello world")
        else:
            # User is not authenticated
            return redirect('users:request-code')


class RequestCodePage(View):
    def get(self, request):
        form = EmailForm()
        return render(request, "users/request_code.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = EmailForm(request.POST)
        if form.is_valid():
            api_url = request.build_absolute_uri(reverse('users-api:request-code'))
            response = requests.post(api_url, json=form.cleaned_data)
            if response.status_code == 201:
                request.session['email'] = form.cleaned_data['email']
                return redirect('users:verify-code')
            else:
                return JsonResponse(response.json(), status=response.status_code)
        return render(request, "users/request_code.html", {"form": form})


class VerifyCodePage(View):
    def get(self, request):
        email = request.session.get('email', "")
        form = CodeVerificationForm(initial={'email': email})
        return render(request, 'users/verify_code.html', {'form': form})

    def post(self, request):
        form = CodeVerificationForm(request.POST)
        if form.is_valid():
            api_url = request.build_absolute_uri(reverse('users-api:verify-code'))
            response = requests.post(api_url, json=form.cleaned_data)
            if response.status_code == 302:
                return redirect('users:home')
            elif response.status_code == 200:
                return redirect('users:sign-up')
            else:
                return JsonResponse(response.json(), status=response.status_code)


class SignUpPage(View):
    def get(self, request):
        email = request.session.get('email', "")
        if not email:
            return redirect('users:request-code')

        form = SignUpForm()
        return render(request, "users/sign_up.html", {"form": form})

    def post(self, request):
        email = request.session.get('email', "")
        if not email:
            return redirect('users:request-code')

        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                data = form.cleaned_data
                data['email'] = email
                api_url = request.build_absolute_uri(reverse('users-api:sign-up'))
                response = requests.post(api_url, json=data)
                if response.status_code == 200:
                    return redirect('users:home')  # Redirect to home or another page on success
                else:
                    form.add_error(None, "An error occurred. Please try again.")
            except requests.exceptions.RequestException as e:
                form.add_error(None, "A connection error occurred. Please try again.")

        return render(request, 'users/sign_up.html', {'form': form})


