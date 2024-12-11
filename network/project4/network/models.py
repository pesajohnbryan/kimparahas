from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser, User
from django.db import models


class User(AbstractUser):
    name = models.CharField(max_length=100, default="user", null=True , blank=True)
    bio = models.CharField(max_length=200, null=True, blank=True)
    link = models.URLField(max_length=100, null=True, blank=True)
    is_followed = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to="network/", default="network/profile.png",null=True)
    cover = models.ImageField(upload_to="network/", default="network/cover.png",null=True)
    
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    post = models.TextField(max_length=200, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)
    reposts = models.ManyToManyField(User, related_name="reposted_posts", blank=True)

    def __str__(self):
        return self.post[:20]

    def like_count(self):
        return self.likes.count()
    
class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post}"

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_likes", null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_likes", null=True) 
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.user.username} liked {self.post.id}"


class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
    def __str__(self):
        return f"{self.follower} follows {self.following}"