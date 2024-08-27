# serializers.py
from rest_framework import serializers
from .models import Gmail_Message, Recevoir_Message, Envoyer_Message, Categorie_Gmail
from accounts.models import AppUser

class GmailCompteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = '__all__'

class GmailMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gmail_Message
        fields = '__all__'

# serializers.py
from rest_framework import serializers
from .models import Gmail_Message, Recevoir_Message, Envoyer_Message, Categorie_Gmail
from accounts.models import AppUser

class GmailCompteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = '__all__'

class GmailMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gmail_Message
        fields = '__all__'

class RecevoirMessageSerializer(serializers.ModelSerializer):
    message_date = serializers.DateTimeField(source='message.date', read_only=True)
    message_contenu = serializers.CharField(source='message.Contenu', read_only=True)
    sender_email = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='message.categorie.Contenu', read_only=True)

    class Meta:
        model = Recevoir_Message
        fields = ['id', 'message_date', 'message_contenu', 'sender_email', 'category_name']
    
    def get_sender_email(self, obj):
        # Retrieve the email of the sender associated with this message
        envoyer_message = obj.message.envoyer_message_set.first()
        if envoyer_message:
            return envoyer_message.user.email
        return None

class EnvoyerMessageSerializer(serializers.ModelSerializer):
    message = GmailMessageSerializer()

    class Meta:
        model = Envoyer_Message
        fields = '__all__'

class CategorieGmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie_Gmail
        fields = '__all__'


class EnvoyerMessageSerializer(serializers.ModelSerializer):
    message = GmailMessageSerializer()

    class Meta:
        model = Envoyer_Message
        fields = '__all__'

class CategorieGmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie_Gmail
        fields = '__all__'
