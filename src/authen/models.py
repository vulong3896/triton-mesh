from django.db import models
import uuid
from orchestrator.models import Tag, Model, ModelVersion

# Create your models here.
class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class RBACAccessToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_tokens')
    name = models.CharField(max_length=128)  # Token name field added
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True) # Null means never expire

    tags = models.ManyToManyField(Tag, related_name='tokens', blank=True)
    ai_models = models.ManyToManyField(Model, related_name='tokens', blank=True)
    versions = models.ManyToManyField(ModelVersion, related_name='tokens', blank=True)

    def __str__(self):
        return f"Token {self.token_name} for {self.user.username} (expires {self.expires_at})"
