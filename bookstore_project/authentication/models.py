from django.contrib.auth.models import AbstractUser
from django.db import models
import logging

logger = logging.getLogger(__name__)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)

    username = models.CharField(max_length=50, unique=True)
    
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            logger.info(f"New user registered: {self.username} (ID: {self.pk})")
        else:
            logger.info(f"User updated: {self.username} (ID: {self.pk})")


class UserActivity(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        logger.info(f"User activity: {self.user.username} - {self.action} at {self.timestamp}")
