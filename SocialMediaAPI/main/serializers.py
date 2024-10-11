from rest_framework import serializers
from .models import CustomUser, Profile, Post, Comment, Like, Notification, Follow
from rest_framework.response import Response
from rest_framework import status


# USER RELATED SERIALIZERS
class ListCreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "email", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = CustomUser(
            email=validated_data["email"], username=validated_data["username"]
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["email", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def update(self, instance, validated_data):
        authenticated_user = self.context.get("request").user
        if authenticated_user == instance:
            username = validated_data.get("username", instance.username)
            email = validated_data.get("email", instance.email)
            password = validated_data.get("password", instance.password)

            instance.username = username
            instance.email = email
            instance.set_password(password)
            instance.save()
            return instance
        raise serializers.ValidationError(
            {"detail": "You are not authorized to modify this user."}
        )


# PROFILE RELATED SERIALIZERS
class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ["user"]

    def update(self, instance, validated_data):
        authenticated_user = self.context.get("request").user
        profile_owner = instance.user
        if authenticated_user == profile_owner:
            bio = validated_data.get("bio", instance.bio)
            instance.bio = bio
            instance.save()
            return instance
        raise serializers.ValidationError(
            {"detail": "You are not authorized to modify this profile."}
        )


# POST RELATED SERIALIZERS
class ListPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"


class CreatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        exclude = ["author"]


class UpdateDeletePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        exclude = ["author"]

    def update(self, instance, validated_data):
        authenticated_user = self.context.get("request").user
        if authenticated_user == instance.author:
            content = validated_data.get("content", instance.content)
            instance.content = content
            instance.save()
            return instance
        raise serializers.ValidationError(
            {"detail": "You are not authorized to modify this post."}
        )


# COMMENT RELATED SERIALIZERS
class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        exclude = ["author"]


class ListCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"


class UpdateDeleteCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        exclude = ["author", "post"]

    def update(self, instance, validated_data):
        authenticated_user = self.context.get("request").user
        if authenticated_user == instance.author:
            content = validated_data.get("content", instance.content)
            instance.content = content
            instance.save()
            return instance
        raise serializers.ValidationError(
            {"detail": "You are not authorized to modify this comment."}
        )


# LIKE RELATED SERIALIZERS
class ListCreateDeleteLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = "__all__"
        read_only_fields = ["user", "post"]


# FOLLOW RELATED SERIALIZERS
class ListCreateFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = "__all__"
        read_only_fields = ["follower", "following"]


class DeleteFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = "__all__"


# NOTIFICATIONS RELATED SERIALIZERS
class ListNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"