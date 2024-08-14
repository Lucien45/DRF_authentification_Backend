from django.db import models

# Create your models here.
class Post(models.Model):
    titre = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='_posts')
    
    def __str__(self):
        return self.titre