from datetime import datetime
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

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["timestamp"] = datetime.strftime(
            instance.timestamp, "%Y-%m-%d %H:%M"
        )
        representation["author_name"] = str(instance.author)

        return representation


class CreatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        exclude = ["author"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["timestamp"] = datetime.strftime(
            instance.timestamp, "%Y-%m-%d %H:%M"
        )
        return representation


class UpdateDeletePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        exclude = ["author"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["timestamp"] = datetime.strftime(
            instance.timestamp, "%Y-%m-%d %H:%M"
        )
        return representation

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

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["created_at"] = datetime.strftime(
            instance.created_at, "%Y-%m-%d %H:%M"
        )
        representation["updated_at"] = datetime.strftime(
            instance.created_at, "%Y-%m-%d %H:%M"
        )
        representation["post"] = str(instance.post)
        representation["comment_by"] = str(instance.author)

        return representation


class ListCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["created_at"] = datetime.strftime(
            instance.created_at, "%Y-%m-%d %H:%M"
        )
        representation["updated_at"] = datetime.strftime(
            instance.created_at, "%Y-%m-%d %H:%M"
        )
        representation["post"] = str(instance.post)
        representation["author_name"] = str(instance.author)

        return representation


class UpdateDeleteCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        exclude = ["author", "post"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["created_at"] = datetime.strftime(
            instance.created_at, "%Y-%m-%d %H:%M"
        )
        representation["updated_at"] = datetime.strftime(
            instance.created_at, "%Y-%m-%d %H:%M"
        )

        return representation

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

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["created_at"] = datetime.strftime(
            instance.created_at, "%Y-%m-%d %H:%M"
        )
        representation["liked_by"] = str(instance.user)
        representation["post_info"] = str(instance.post)

        return representation


# FOLLOW RELATED SERIALIZERS
class ListCreateFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = "__all__"
        read_only_fields = ["follower", "following"]

    def to_representation(self, instance):
        authenticated_user = self.context.get("request").user
        user_followed = instance.following
        representation = super().to_representation(instance)
        representation["created_at"] = datetime.strftime(
            instance.created_at, "%Y-%m-%d %H:%M"
        )

        detail_info = ""
        if user_followed == authenticated_user:
            detail_info = f"{str(instance.follower)} follows you"
        else:
            detail_info = f"Following {str(instance.following)}"

        representation["detail"] = detail_info

        return representation


class DeleteFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = "__all__"


# NOTIFICATIONS RELATED SERIALIZERS
class ListNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["recipient", "sender", "notification_type", "created_at"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["recipient_name"] = str(instance.recipient)
        representation["sender_name"] = str(instance.sender)
        representation["created_at"] = datetime.strftime(
            instance.created_at, "%Y-%m-%d %H:%M"
        )

        if instance.post:
            representation["post"] = str(instance.post)
        elif instance.follow:
            representation["follow"] = str(instance.follow)
        elif instance.comment:
            representation["comment"] = str(instance.comment)

        return representation
