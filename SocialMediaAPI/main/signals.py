from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Follow, Like, Comment, Notification, Post


@receiver(post_save, sender=Post)
def create_post_notification(sender, instance, created, **kwargs):
    if created:
        user = instance.author
        follow_instances = user.followers.all()
        for follow_instance in follow_instances:
          Notification.objects.create(
              recipient=follow_instance.follower,
              sender=user,
              notification_type='post',
              post=instance
          )

@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if created:
        user = instance.author
        follow_instances = user.followers.all()
        for follow_instance in follow_instances:
          Notification.objects.create(
              recipient=follow_instance.follower,
              sender=user,
              notification_type='comment',
              comment=instance
          )

@receiver(post_save, sender=Follow)
def create_like_notification(sender, instance, created, **kwargs):
    if created:
        user = instance.follower
        follow_instances = user.followers.all()
        for follow_instance in follow_instances:
          Notification.objects.create(
              recipient=follow_instance.follower,
              sender=user,
              notification_type='follow',
              follow=instance
          )
