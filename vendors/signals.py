from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import LoginStreak

@receiver(user_logged_in)
def update_login_streak(sender, request, user, **kwargs):
    streak, created = LoginStreak.objects.get_or_create(vendor=user)
    streak.update()
