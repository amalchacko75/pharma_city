from django.contrib.auth.backends import ModelBackend
from accounts.models import AdminUser


class AdminUserBackend(ModelBackend):
    """
    Authenticate AdminUser using email and password
    """
    def authenticate(self, request, email=None, password=None, **kwargs):
        if email is None or password is None:
            return None
        try:
            user = AdminUser.objects.get(email=email)
        except AdminUser.DoesNotExist:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
