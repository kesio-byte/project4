from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass 

# ---- The User model inherits from AbstractUser clas -------
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

#---------- Many-to-many relatioship for likes ---------
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}" # Display the username and the first 30 characters of the Post model.

# ------- The Post model has a ForeignKey , a TextField for contnt, a DateTimeField for timestamp, and a ManyToManyField for likes. -------
class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
