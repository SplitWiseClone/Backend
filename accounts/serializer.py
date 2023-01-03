from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .utils import Util
class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'password2')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords must match'})
        validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        return user


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ('email', 'password')


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email')


class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True, max_length=255, min_length=8)
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True, max_length=255, min_length=8)
    class Meta:
        model = User
        fields = ('password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords must match'})

        user = self.context.get('user')
        user.set_password(attrs['password'])
        user.save()
        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2, max_length=255)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        print('email: ', email)
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            link = 'http://localhost:3000/api/user/reset/' + uidb64 + '/' + token
            print('Password reset link', link)
            Util.send_email(data={'email_body': 'Click Following link to reset your password'+link, 'to_email': user.email, 'email_subject': 'Reset your password'})
            return attrs
        else:
            raise serializers.ValidationError({'email': 'Email is not registered'})

class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True, max_length=255, min_length=8)
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True, max_length=255, min_length=8)

    class Meta:
        fields = ['password', 'password2']

    def validate(self, attrs):
        try:
            if attrs['password'] != attrs['password2']:
                raise serializers.ValidationError({'password': 'Passwords must match'})
            uid = self.context.get('uid')
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, self.context.get('token')):
                raise serializers.ValidationError({'token': 'Token is not valid or expired, please request a new one'})
            user.set_password(attrs['password'])
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, self.context.get('token'))
            raise serializers.ValidationError({'token': 'Token is not valid or expired, please request a new one'})

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance
