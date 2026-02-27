from django.db import models

# Create your models here.

class CodeReview(models.Model):
    code = models.TextField(max_length=1000)
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review {self.id}"