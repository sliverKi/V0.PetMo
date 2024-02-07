from django.db import models

class History(models.Model):
    user=models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="user_history"
    )
    query = models.CharField(max_length=255)
    searched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}: {self.query}"
