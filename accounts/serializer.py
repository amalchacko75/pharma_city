from rest_framework import serializers
from django.contrib.auth import authenticate
from accounts.models import AdminUser


class AdminUserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = AdminUser
        fields = ('id', 'email', 'name', 'role', 'password', 'facility')

    def validate_role(self, value):
        if value not in ['pharmacist', 'doctor']:
            raise serializers.ValidationError("Only pharmacist or doctor admin can signup here.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = AdminUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


class AdminUserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("User is inactive")

        # For super_admin, attach automatic access to both roles
        attrs['user'] = user
        return attrs
