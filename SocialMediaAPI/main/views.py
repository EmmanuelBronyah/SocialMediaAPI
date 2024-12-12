from django.shortcuts import render
from . import serializers
from rest_framework import generics
from .models import CustomUser, Profile, Post, Comment, Like, Follow, Notification
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, time as dt_time
from rest_framework.pagination import PageNumberPagination
from .posts_comments_functions import *
from rest_framework import permissions
from django.core.exceptions import ValidationError as django_validation_error


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_query_param = "page_size"
    max_page_size = 10

    def get_paginated_response(self, data):
        return Response(
            {
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "count": self.page.paginator.count,
                "results": data,
            }
        )


# USER RELATED VIEWS
class ListCreateUserView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = serializers.ListCreateUserSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        Profile.objects.create(user=user)


class RetrieveUpdateUserView(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = serializers.UpdateUserSerializer
    lookup_field = "pk"
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# PROFILE RELATED VIEWS
class RetrieveUpdateProfileView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = serializers.UpdateProfileSerializer
    lookup_field = "pk"
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# POST RELATED VIEWS
class ListPostView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.ListPostSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_posts(self):
        user = self.request.user
        following_users = Follow.objects.filter(follower=user).values_list(
            "following", flat=True
        )
        posts = Post.objects.filter(author__in=following_users).order_by(
            "-timestamp"
        ) | Post.objects.filter(author=user).order_by("-timestamp")
        return posts

    def get_queryset(self):
        sort_by = self.request.query_params.get("sort_by")
        if sort_by is None:
            posts = self.get_posts()
            return posts

        match sort_by:
            case "likes":
                posts = self.get_posts()
                post_with_likes = list(map(get_post_likes, posts))
                sorted_post_with_likes = sorted(
                    post_with_likes,
                    key=lambda post_data: post_data["total_likes"],
                    reverse=True,
                )
                posts = list(map(get_sorted_posts, sorted_post_with_likes))
                return posts
            case "comments":
                posts = self.get_posts()
                post_with_comments = list(map(get_post_comments, posts))
                sorted_post_with_comments = sorted(
                    post_with_comments,
                    key=lambda post_data: post_data["total_comments"],
                    reverse=True,
                )
                posts = list(map(get_sorted_posts, sorted_post_with_comments))
                return posts


class CreatePostView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.CreatePostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class SearchPostView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.ListPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Post.objects.all()

        date = self.request.query_params.get("date")
        time = self.request.query_params.get("time")
        keyword = self.request.query_params.get("keyword")

        try:
            if date:
                queryset = queryset.filter(timestamp__date=date)
                return queryset
            if keyword:
                queryset = queryset.filter(content__icontains=keyword)
                return queryset
            if time:
                try:
                    hour, minute = time.split(":")
                    queryset = queryset.filter(
                        timestamp__time=dt_time(int(hour), int(minute))
                    )
                    return queryset
                except ValueError as e:
                    raise ValidationError({"detail": "Invalid time format."})
        except django_validation_error as e:
            raise ValidationError({"detail": str(e)})


class RetrieveUpdateDeletePostView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.UpdateDeletePostSerializer
    lookup_field = "pk"
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

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
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs.get("post_id")
        return Comment.objects.filter(post__id=post_id)


class CreateCommentView(generics.ListCreateAPIView):
    serializer_class = serializers.CreateCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return user.comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class UpdateCommentView(generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.UpdateDeleteCommentSerializer
    lookup_field = "pk"
    permission_classes = [permissions.IsAuthenticated]


class DeleteCommentView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.UpdateDeleteCommentSerializer
    lookup_field = "pk"
    permission_classes = [permissions.IsAuthenticated]

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
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        return user.likes.all()

    def perform_create(self, serializer):
        try:
            post_id = self.kwargs.get("post_id")
            post = Post.objects.get(id=post_id)
            like = Like.objects.get(user=self.request.user, post=post_id)
            if like:
                raise ValidationError({"detail": "You have already liked this post."})
        except Like.DoesNotExist:
            serializer.save(user=self.request.user, post=post)
        except Post.DoesNotExist:
            raise ValidationError(
                {"detail": f"Post with id '{post_id}' does not exist."}
            )


class DeleteLikeView(generics.DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.ListCreateDeleteLikeSerializer
    lookup_field = "pk"
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        try:
            like = Like.objects.get(user=self.request.user, post=instance)
            like_owner = like.user
            authenticated_user = self.request.user
            if like_owner == authenticated_user:
                like.delete()
            else:
                raise PermissionDenied(
                    {"detail": "You are not authorized to unlike this post."}
                )
        except Like.DoesNotExist:
            raise ValidationError({"detail": "You have not liked this post."})


# FOLLOW RELATED VIEWS
class ListFollowerView(generics.ListAPIView):
    serializer_class = serializers.ListCreateFollowSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return user.followers.all()


class ListCreateFollowView(generics.ListCreateAPIView):
    serializer_class = serializers.ListCreateFollowSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticated]

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
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        try:
            follow = Follow.objects.get(follower=self.request.user, following=instance)
            follow_owner = follow.follower
            authenticated_user = self.request.user
            if follow_owner == authenticated_user:
                follow.delete()
            else:
                raise PermissionDenied(
                    {
                        "detail": "You are not authorized to perform this unfollow action."
                    }
                )
        except Follow.DoesNotExist:
            raise ValidationError(
                {
                    "detail": "Cannot execute unfollow operation on a user you are not following."
                }
            )


# NOTIFICATIONS RELATED VIEWS
class ListNotification(generics.ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = serializers.ListNotificationSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        following_users = Follow.objects.filter(follower=user).values_list(
            "following", flat=True
        )
        notifications = Notification.objects.filter(sender__in=following_users)
        return notifications
