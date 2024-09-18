from rest_framework import generics
from rest_framework import status
from . import models
from rest_framework.permissions import IsAuthenticated, AllowAny
from . import serializers
from rest_framework.response import Response
# Create your views here.


class ListCreateUserAPIView(generics.ListCreateAPIView):
    queryset = models.User.objects.all()
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.CreateUserSerializer  
        return serializers.UserSerializer


class RetrieveUserAPIView(generics.RetrieveAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    # permission_classes = [IsAuthenticated]
    lookup_field = "id"


class ListCreateGroupAPIView(generics.ListCreateAPIView):
    queryset = models.Group.objects.all()
    serializer_class = serializers.GroupSerializer
    # permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]  
        return [AllowAny()]
    
    def perform_create(self, serializer):
        group = serializer.save(owner=self.request.user)
        group.users.add(self.request.user)
        
        
        users = self.request.data.get("users", [])
        for user_id in users:
            user = models.User.objects.get(id=user_id)
            user.groups.add(group)
        
        group.save()
        return Response({"message": "Group created successfully!"}, status=status.HTTP_201_CREATED)
        

class DestroyGroupAPIView(generics.DestroyAPIView):
    queryset = models.Group.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    
    def preform_destroy(self):
        try:
            group_id = self.kwargs['id']
            group = models.Group.objects.get(id=group_id)
            if group.owner == self.request.user:
                group.delete()
                return Response({"message": "Group deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error":"You don't have permission to delete this group"}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"error":str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ListCreateMessageAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.MessageSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]  # Only authenticated users can create
        return [AllowAny()]
    
    def perform_create(self, serializer, *args, **kwargs):
        try:
            group_id =self.kwargs['group_id']
            group = models.Group.objects.get(id=group_id)
            serializer.save(author=self.request.user, group=group)
            return Response({"message": "Message created successfully!"}, status=status.HTTP_201_CREATED)
        except models.Group.DoesNotExist:
            raise serializers.ValidationError({"error": "Group not found"})
        
    def get_queryset(self):
        group_id = self.kwargs.get('group_id')
        try:
            group = models.Group.objects.get(id=group_id)
        except models.Group.DoesNotExist:
            return Response({"error": "Group does not exist!"}, status=status.HTTP_404_NOT_FOUND)
        return models.Message.objects.filter(group=group)


class RetriveUserGroupsAPIView(generics.ListAPIView):
    queryset = models.Group.objects.all()
    serializer_class = serializers.GroupSerializer
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        user = self.request.user
        user_groups = user.groups.all()
        owned_groups = models.Group.objects.filter(owner=user)
        all_groups = (user_groups | owned_groups).distinct()
        
        serializer = self.get_serializer(all_groups, many=True)
        
        return Response({"groups":serializer.data}, status=status.HTTP_200_OK)
    
class RetriveCurrentUserAPIView(generics.RetrieveAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(user)
        
        return Response({"user":serializer.data}, status=status.HTTP_200_OK)