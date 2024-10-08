import random
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from .serializers import EmailSerializer, CodeVerificationSerializer, SignUpSerializer
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class RequestCodeView(APIView):
    """
    View to handle the first step where a user enters their email.
    """

    @swagger_auto_schema(
        request_body=EmailSerializer,
        responses={
            201: openapi.Response(
                description="A code has been sent to your email.",
                examples={"application/json": {"message": "A code has been sent to your email.", "verify_url": "/verify-code/"}}
            ),
            400: openapi.Response(description="Invalid email.")
        }
    )
    def post(self, request):
        serializer = EmailSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = ''.join([str(random.randint(0, 9)) for _ in range(8)])

            user, created = User.objects.get_or_create(email=email)
            if created:
                user.is_active = False  # Mark user inactive until verified
            user.set_password(code)
            user.code_created_at = timezone.now()
            user.save()

            send_mail(
                "Your Login Code",
                f"Your login code is {code}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            response_data = {
                "message": "A code has been sent to your email.",
                "verify_url": request.build_absolute_uri('/verify-code/')
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CodeVerificationView(APIView):
    """
    View to handle code verification.
    """

    @swagger_auto_schema(
        request_body=CodeVerificationSerializer,
        responses={
            200: openapi.Response(
                description="Login successful, redirecting to home or sign up.",
                examples={"application/json": {"message": "Login successful, redirecting to home", "access_token": "<JWT_TOKEN>", "refresh_token": "<REFRESH_TOKEN>", "verify_url": "/home/"}}
            ),
            400: openapi.Response(description="Invalid email or code."),
            302: openapi.Response(description="Redirecting to home.")
        }
    )
    def post(self, request):
        serializer = CodeVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "Invalid email or code."}, status=status.HTTP_400_BAD_REQUEST)

            expiration_time = user.code_created_at + timezone.timedelta(minutes=2)
            if timezone.now() > expiration_time:
                return Response({'error': 'The code has expired. Please request a new code.'},
                                status=status.HTTP_400_BAD_REQUEST)

            if user.check_password(code):
                if user.is_active:
                    refresh = RefreshToken.for_user(user)
                    access_token = str(refresh.access_token)
                    refresh_token = str(refresh)

                    response_data = {
                        "message": "Login successful, redirecting to home",
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "verify_url": request.build_absolute_uri('/home/')
                    }

                    return Response(response_data, status=status.HTTP_302_FOUND)
                else:
                    response_data = {
                        "message": "New user, redirecting to signup.",
                        "verify_url": request.build_absolute_uri('/sign-up/')
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid email or code.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignUpView(APIView):
    """
    View to handle the sign up process.
    """

    @swagger_auto_schema(
        request_body=SignUpSerializer,
        responses={
            200: openapi.Response(
                description="Login successful, redirecting to home.",
                examples={"application/json": {"message": "Login successful, redirecting to home", "access_token": "<JWT_TOKEN>", "refresh_token": "<REFRESH_TOKEN>", "verify_url": "/home/"}}
            ),
            400: openapi.Response(description="User does not exist or already active.")
        }
    )
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        if user.is_active:
            return Response({'error': 'User is already active.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SignUpSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            user.is_active = True
            user.save()

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            response_data = {
                "message": "Login successful, redirecting to home",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "verify_url": request.build_absolute_uri('/home/')
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActiveUserView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        responses={
            200: openapi.Response(description="User is active."),
            403: openapi.Response(description="User is not active.")
        }
    )
    def get(self, request):
        user = request.user
        if user.is_active:
            return Response({'message': f'User {user.email} is active.'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': f'User {user.email} is not active.'}, status=status.HTTP_403_FORBIDDEN)
