from django.urls import path
from .views import *
from rest_framework.authtoken import views as drf_views

urlpatterns = [
    path('api-token-auth/', drf_views.obtain_auth_token, name='api_token_auth'),
    
    path('user/', ListCreateUserAPIView.as_view(), name="user"),
    path('user/<int:id>/', RetrieveUserAPIView.as_view(), name="user-retrieve"),
    path("group/", ListCreateGroupAPIView.as_view(), name="group"),
    path("group/<int:id>/delete/", DestroyGroupAPIView.as_view(), name="group-destroy"),
    path("group/<int:group_id>/messages/", ListCreateMessageAPIView.as_view(), name="group-message"),
    path("user/groups/", RetriveUserGroupsAPIView.as_view(), name="user-groups"),
    path("user/me", RetriveCurrentUserAPIView.as_view(), name="user-me")
    
]