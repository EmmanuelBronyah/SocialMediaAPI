from django.shortcuts import render
from .serializers import (
    ListCreateUserSerializer,
    UpdateUserSerializer,
    UpdateProfileSerializer,
    CreatePostSerializer,
    UpdateDeletePostSerializer,
    ListPostSerializer,
    CreateCommentSerializer,
    UpdateDeleteCommentSerializer,
    ListCommentSerializer,
    ListCreateDeleteLikeSerializer,
    ListCreateFollowSerializer,
    DeleteFollowSerializer,
)
from rest_framework.generics import (
    CreateAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
    ListCreateAPIView,
    UpdateAPIView,
    DestroyAPIView,
)
from .models import CustomUser, Profile, Post, Comment, Like, Follow, Notification
from rest_framework.exceptions import PermissionDenied, ValidationError


# USER RELATED VIEWS
class ListCreateUserView(ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = ListCreateUserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        Profile.objects.create(user=user)


class RetrieveUpdateUserView(RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UpdateUserSerializer
    lookup_field = "pk"


# PROFILE RELATED VIEWS
class RetrieveUpdateProfileView(RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = UpdateProfileSerializer
    lookup_field = "pk"


# POST RELATED VIEWS
class ListPostView(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = ListPostSerializer


class CreatePostView(CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = CreatePostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class RetrieveUpdateDeletePostView(RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = UpdateDeletePostSerializer
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
class ListCommentView(ListAPIView):
    serializer_class = ListCommentSerializer

    def get_queryset(self):
        post_id = self.kwargs.get("post_id")
        return Comment.objects.filter(post__id=post_id)


class CreateCommentView(ListCreateAPIView):
    serializer_class = CreateCommentSerializer

    def get_queryset(self):
        user = self.request.user
        return user.comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class UpdateCommentView(UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = UpdateDeleteCommentSerializer
    lookup_field = "pk"


class DeleteCommentView(DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = UpdateDeleteCommentSerializer
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
class ListCreateLikeView(ListCreateAPIView):
    serializer_class = ListCreateDeleteLikeSerializer

    def get_queryset(self):
        user = self.request.user
        return user.likes.all()

    def perform_create(self, serializer):
        post_id = self.kwargs.get("post_id")
        post = Post.objects.get(id=post_id)
        serializer.save(user=self.request.user, post=post)


class DeleteLikeView(DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = ListCreateDeleteLikeSerializer
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
class ListFollowerView(ListAPIView):
    serializer_class = ListCreateFollowSerializer

    def get_queryset(self):
        user = self.request.user
        return user.followers.all()


class ListCreateFollowView(ListCreateAPIView):
    serializer_class = ListCreateFollowSerializer

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


class DeleteFollowView(DestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = DeleteFollowSerializer
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
