from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

urlpatterns = [
    # retrieve token
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # create user
    path("user/", views.ListCreateUserView.as_view(), name="list_create_user"),
    # retrieve or update a profile or user
    path(
        "user/<int:pk>/",
        views.RetrieveUpdateUserView.as_view(),
        name="retrieve_update_user",
    ),
    path(
        "profile/<int:pk>/",
        views.RetrieveUpdateProfileView.as_view(),
        name="retrieve_update_profile",
    ),
    # retrieve, create, update, or delete a post
    path("posts/", views.ListPostView.as_view(), name="list_post"),
    path("create-post/", views.CreatePostView.as_view(), name="create_post"),
    path("search-post/", views.SearchPostView.as_view(), name="search-post"),
    path(
        "post/<int:pk>/",
        views.RetrieveUpdateDeletePostView.as_view(),
        name="retrieve_update_delete_post",
    ),
    # create, update, or delete a comment
    path("comments/", views.CreateCommentView.as_view(), name="create_comment"),
    path(
        "comments/<int:post_id>/", views.ListCommentView.as_view(), name="list_comment"
    ),
    path(
        "comment/<int:pk>/edit/",
        views.UpdateCommentView.as_view(),
        name="update_comment",
    ),
    path(
        "comment/<int:pk>/delete/",
        views.DeleteCommentView.as_view(),
        name="delete_comment",
    ),
    # like or unlike a post
    path("like/", views.ListCreateLikeView.as_view(), name="list_like"),
    path(
        "like/<int:post_id>/",
        views.ListCreateLikeView.as_view(),
        name="list_create_like",
    ),
    path("like/<int:pk>/delete/", views.DeleteLikeView.as_view(), name="delete_like"),
    # retrieve all users you are following, follow or unfollow users
    path("following-list/", views.ListCreateFollowView.as_view(), name="list_follow"),
    path("follower-list/", views.ListFollowerView.as_view(), name="list_follow"),
    path(
        "follow/<int:follower_id>/",
        views.ListCreateFollowView.as_view(),
        name="list_create_follow",
    ),
    path(
        "follow/<int:pk>/delete/",
        views.DeleteFollowView.as_view(),
        name="delete_follow",
    ),
    # list notifications
    path("notifications/", views.ListNotification.as_view(), name="list_notification"),
]
