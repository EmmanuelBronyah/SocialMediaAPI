from django.contrib import admin

from .models import CustomUser, Profile, Post, Comment, Like, Follow, Notification


admin.site.register(CustomUser)
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Follow)
admin.site.register(Notification)
