from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from .models import User


class SprigSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Ensure Google sign-in users get a valid username and farmer role."""

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        if not user.username:
            user.username = self._generate_unique_username(data.get("email", ""))
        user.role = User.Role.FARMER
        return user

    def _generate_unique_username(self, email):
        base = (email.split("@")[0] if email else "user")[:30]
        username = base
        counter = 1
        while User.objects.filter(username=username).exists():
            suffix = str(counter)
            username = f"{base[: 30 - len(suffix)]}{suffix}"
            counter += 1
        return username
