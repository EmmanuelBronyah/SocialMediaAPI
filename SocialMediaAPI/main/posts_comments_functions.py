from .models import Like, Comment


def get_post_likes(post):
    likes = Like.objects.filter(post=post)
    number_of_likes = likes.count()
    return {"post": post, "total_likes": number_of_likes}


def get_sorted_posts(post_data):
    return post_data["post"]


def get_post_comments(post):
    comments = Comment.objects.filter(post=post)
    number_of_comments = comments.count()
    return {"post": post, "total_comments": number_of_comments}
