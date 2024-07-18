from django.db import models
from django.contrib.auth.models import User


class Answers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video_title = models.CharField(max_length=300)
    question = models.TextField()
    video_link = models.URLField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.video_title
