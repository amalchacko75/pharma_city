from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# from accounts.models import AdminUser
from accounts.serializer import (
    AdminUserSignupSerializer, AdminUserLoginSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class AdminSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AdminUserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "user": AdminUserSignupSerializer(user).data,
                "tokens": get_tokens_for_user(user)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminLoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AdminUserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # For super_admin, they get access to all roles automatically
        roles = [user.role]
        if user.role == 'super_admin':
            roles = ['pharmacy_admin', 'doctor_admin']

        return Response({
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "accessible_roles": roles
            },
            "tokens": get_tokens_for_user(user)
        })
