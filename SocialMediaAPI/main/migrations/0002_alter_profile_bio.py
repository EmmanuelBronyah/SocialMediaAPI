# Generated by Django 5.1.1 on 2024-10-05 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="bio",
            field=models.TextField(blank=True, null=True),
        ),
    ]