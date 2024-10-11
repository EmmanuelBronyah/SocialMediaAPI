# Social Media API
## Overview
This project is a Social Media API built using Django and Django REST Framework. It includes core functionalities for managing users, posts, comments, likes, follows, notifications, and user authentication. The goal of this project is to provide a backend for a social media platform where users can interact by creating posts, following other users, commenting on posts, liking content, and receiving notifications for various activities.

## Features
1. User Management
  User registration, login, and profile management.
2. JWT-based authentication for securing endpoints.
3. Profile creation with bio and profile picture (stored in PostgreSQL).
4. Post Management
  Full CRUD operations (create, read, update, delete) for posts.
5. Follow System
  Follow and unfollow other users.
  Prevent users from following themselves.
6. Display a feed of posts from followed users.
7. Comment & Like System
  Comment on posts and view comments.
8. Like and unlike posts.
  Prevent users from liking the same post multiple times.
9. Notifications
  Users receive notifications for likes, comments, and new followers.
  Notifications system is implemented to ensure users stay informed.

## Tech Stack
1. Backend Framework: Django, Django REST Framework
2. Database: PostgreSQL
3. Authentication: JWT (JSON Web Tokens) via djangorestframework-simplejwt

## Installation
## Prerequisites
1. Python 3.x
2. PostgreSQL
3. Virtual Environment (optional but recommended)
