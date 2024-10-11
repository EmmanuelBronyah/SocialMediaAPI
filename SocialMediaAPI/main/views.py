from django.shortcuts import render
from . import serializers
from rest_framework import generics
from .models import CustomUser, Profile, Post, Comment, Like, Follow, Notification
from rest_framework.exceptions import PermissionDenied, ValidationError


# USER RELATED VIEWS
class ListCreateUserView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = serializers.ListCreateUserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        Profile.objects.create(user=user)


class RetrieveUpdateUserView(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = serializers.UpdateUserSerializer
    lookup_field = "pk"


# PROFILE RELATED VIEWS
class RetrieveUpdateProfileView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = serializers.UpdateProfileSerializer
    lookup_field = "pk"


# POST RELATED VIEWS
class ListPostView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.ListPostSerializer
    
    # def get_queryset(self):
      


class CreatePostView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.CreatePostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class RetrieveUpdateDeletePostView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.UpdateDeletePostSerializer
    lookup_field = "pk"

    def perform_destroy(self, instance):
        post_owner = instance.author
        authenticated_user = self.request.user
        if post_owner == authenticated_user:
            instance.delete()
        else:
            raise PermissionDenied(
                {"detail": "You are not authorized to delete this post."}
            )


# COMMENT RELATED VIEWS
class ListCommentView(generics.ListAPIView):
    serializer_class = serializers.ListCommentSerializer

    def get_queryset(self):
        post_id = self.kwargs.get("post_id")
        return Comment.objects.filter(post__id=post_id)


class CreateCommentView(generics.ListCreateAPIView):
    serializer_class = serializers.CreateCommentSerializer

    def get_queryset(self):
        user = self.request.user
        return user.comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class UpdateCommentView(generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.UpdateDeleteCommentSerializer
    lookup_field = "pk"


class DeleteCommentView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.UpdateDeleteCommentSerializer
    lookup_field = "pk"

    def perform_destroy(self, instance):
        comment_owner = instance.author
        authenticated_user = self.request.user
        if comment_owner == authenticated_user:
            instance.delete()
        else:
            raise PermissionDenied(
                {"detail": "You are not authorized to delete this comment."}
            )


# LIKE RELATED VIEWS
class ListCreateLikeView(generics.ListCreateAPIView):
    serializer_class = serializers.ListCreateDeleteLikeSerializer

    def get_queryset(self):
        user = self.request.user
        return user.likes.all()

    def perform_create(self, serializer):
        post_id = self.kwargs.get("post_id")
        post = Post.objects.get(id=post_id)
        serializer.save(user=self.request.user, post=post)


class DeleteLikeView(generics.DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.ListCreateDeleteLikeSerializer
    lookup_field = "pk"

    def perform_destroy(self, instance):
        like = Like.objects.get(user=self.request.user, post=instance)
        like_owner = like.user
        authenticated_user = self.request.user
        if like_owner == authenticated_user:
            like.delete()
        else:
            raise PermissionDenied(
                {"detail": "You are not authorized to unlike this post."}
            )


# FOLLOW RELATED VIEWS
class ListFollowerView(generics.ListAPIView):
    serializer_class = serializers.ListCreateFollowSerializer

    def get_queryset(self):
        user = self.request.user
        return user.followers.all()


class ListCreateFollowView(generics.ListCreateAPIView):
    serializer_class = serializers.ListCreateFollowSerializer

    def get_queryset(self):
        user = self.request.user
        return user.following.all()

    def perform_create(self, serializer):
        follower_id = self.kwargs.get("follower_id")
        if follower_id == self.request.user.id:
            raise ValidationError({"detail": "You cannot follow yourself."})
        else:
            following = CustomUser.objects.get(id=follower_id)
            serializer.save(follower=self.request.user, following=following)


class DeleteFollowView(generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = serializers.DeleteFollowSerializer
    lookup_field = "pk"

    def perform_destroy(self, instance):
        follow = Follow.objects.get(follower=self.request.user, following=instance)
        follow_owner = follow.follower
        authenticated_user = self.request.user
        if follow_owner == authenticated_user:
            follow.delete()
        else:
            raise PermissionDenied(
                {"detail": "You are not authorized to perform this unfollow action."}
            )


# NOTIFICATIONS RELATED VIEWS
class ListNotification(generics.ListAPIView):
  queryset = Notification.objects.all() 
  serializer_class = serializers.ListNotificationSerializer
  
  def get_queryset(self):
    user = self.request.user
    following_users = Follow.objects.filter(follower=user).values_list('following', flat=True)
    return Notification.objects.filter(sender__in=following_users)