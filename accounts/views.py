# Create your views here.
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializer import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer, UserChangePasswordSerializer, SendPasswordResetEmailSerializer, UserPasswordResetSerializer
from django.contrib.auth import authenticate
from accounts.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken


# Generate a token for the user manually
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserRegistrationView(APIView):
    renderer_classes = (UserRenderer,)

    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = get_tokens_for_user(user)
        if user:
            return Response({'token': token, 'msg': 'Registration Successful'}, status=status.HTTP_201_CREATED)

        # return Response({'msg': 'Registration Successful'})


class UserLoginView(APIView):
    renderer_classes = (UserRenderer,)

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = authenticate(username=email, password=password)
        if user:
            token = get_tokens_for_user(user)
            return Response({'token': token, 'msg': 'Login Successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': {'non_field_errors': ['Email or Password is not valid']}},
                            status=status.HTTP_404_NOT_FOUND)


class UserProfileView(APIView):
    renderer_classes = (UserRenderer,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserChangePasswordView(APIView):
    renderer_classes = (UserRenderer,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Password Changed Successfully'}, status=status.HTTP_200_OK)


class SendPasswordResetEmailView(APIView):
    renderer_classes = (UserRenderer,)

    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Password Reset Email Sent Successfully. Please check your email'},
                        status=status.HTTP_200_OK)


class UserPasswordResetView(APIView):
    renderer_classes = (UserRenderer,)

    def post(self, request, uid, token, format=None):
        serializer = UserPasswordResetSerializer(data=request.data, context={'uid': uid, 'token': token})
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Password Reset Successfully'}, status=status.HTTP_200_OK)
