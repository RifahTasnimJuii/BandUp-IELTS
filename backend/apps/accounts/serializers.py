from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import Profile, User


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'target_band',
            'country',
            'language_preference',
            'timezone',
            'dark_mode',
            'leaderboard_opt_in',
            'exam_instructions_acknowledged',
            'streak_count',
            'last_practice_at',
            'avatar_url',
            'bio',
            'speaking_audio_consent',
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    profile = ProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['email', 'username', 'full_name', 'password', 'password_confirm', 'profile']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': _('Passwords do not match.')})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        profile_data = validated_data.pop('profile', None)
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            full_name=validated_data.get('full_name', ''),
        )
        if profile_data:
            Profile.objects.filter(user=user).update(**profile_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(email=attrs.get('email'), password=attrs.get('password'))
        if not user:
            raise serializers.ValidationError(_('Unable to log in with provided credentials.'))
        if not user.is_active:
            raise serializers.ValidationError(_('User account is disabled.'))
        attrs['user'] = user
        return attrs


class UserMeSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'full_name', 'role', 'auth_provider', 'email_verified', 'is_active', 'profile']
        read_only_fields = ['email', 'role', 'auth_provider', 'email_verified', 'is_active']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        profile = instance.profile
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()
        return instance
