# from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password):
        if not username:
            raise ValueError("username needed!") 
        if not email:
            raise ValueError("email needed!")    
        if not password:
            raise ValueError("password needed!")
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, username, email, password):
        if not username:
            raise ValueError("username needed!") 
        if not email:
            raise ValueError("email needed!")    
        if not password:
            raise ValueError("password needed!")
        
        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user
           
    
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    groups = models.ManyToManyField('Group', related_name='user_groups', blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS  = ["email"]
    objects = CustomUserManager()
    
    def __str__(self) -> str:
        return self.username

class Group(BaseModel):
    name = models.CharField(max_length=30, unique=True)
    users = models.ManyToManyField(User, related_name="user_groups")  # Custom related_name
    owner = models.ForeignKey(User, related_name="owned_groups", on_delete=models.CASCADE)
    massages = models.ManyToManyField("message", related_name="groups")

    def __str__(self):
        return self.name

class Message(BaseModel):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey("Group", on_delete=models.CASCADE, related_name="messages")

