from django.db import models

from accounts.models import *

# Create your models here.
class Categorie_Gmail(models.Model):
    """
    Description: Model Envoyer_Message
    """
    Contenu = models.TextField(max_length=50, unique=True, blank=True, null=True)
    

class Gmail_Message(models.Model):
    """
    Description: Model Gmail_Message
    """
    Contenu = models.TextField(blank=True)
    date = models.DateTimeField(blank=True, null=True)
    categorie = models.ForeignKey(Categorie_Gmail, on_delete=models.CASCADE, blank=True, null=True)


    class Meta:
        pass
    
class Recevoir_Message(models.Model):
    """
    Description: Model Recevoir_Message
    """
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    message = models.ForeignKey(Gmail_Message, on_delete=models.CASCADE)

    class Meta:
        pass

class Envoyer_Message(models.Model):
    """
    Description: Model Envoyer_Message
    """
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    message = models.ForeignKey(Gmail_Message, on_delete=models.CASCADE, related_name='envoyer_message_set')