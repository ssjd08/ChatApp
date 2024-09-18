from rest_framework import serializers
from . import models

class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Group
        fields = ["id", "name", "users", "owner"]
        read_only_fields = ["id", "owner"]


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ["id", "username", "email", "image", "password", "groups"]
        read_only_fields = ["id", "groups"]
        extra_kwargs = {
            'password': {'write_only': True}  
        }
        
    def create(self, validated_data):
        user = models.User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])  # Hash password
        user.save()
        return user
    
class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)
        
    class Meta:
        model = models.User
        fields = ["id", "username", "email", "image", "groups"]
        read_only_fields = ["id", "groups"]



class MessageSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    class Meta:
        model = models.Message
        fields = "__all__"
        read_only_fields = ["id", 'author', 'group']