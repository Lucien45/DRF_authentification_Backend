from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status, viewsets
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split
from rest_framework.authentication import SessionAuthentication
import joblib
import re
import logging
import pandas as pd
from .models import *
from .serializers import *

logger = logging.getLogger(__name__)

# Paths for the model and vectorizer files
MODEL_PATH = r'sample_data/logistic_regression_model.joblib'
VECTORIZER_PATH = r'sample_data/tfidf_vectorizer_regretion.joblib'

# Load the model and vectorizer
loaded_model_rf = joblib.load(MODEL_PATH)
loaded_vectorizer_rf = joblib.load(VECTORIZER_PATH)

# Function to clean text data
def clean_text(text):
    text = re.sub(r'[^a-zA-Z\s]', '', str(text))
    return text.lower()

# ViewSets for CRUD operations
class GmailCompteViewSet(viewsets.ModelViewSet):
    queryset = AppUser.objects.all()
    serializer_class = GmailCompteSerializer

class GmailMessageViewSet(viewsets.ModelViewSet):
    queryset = Gmail_Message.objects.all()
    serializer_class = GmailMessageSerializer

class RecevoirMessageViewSet(viewsets.ModelViewSet):
    queryset = Recevoir_Message.objects.all()
    serializer_class = RecevoirMessageSerializer

class EnvoyerMessageViewSet(viewsets.ModelViewSet):
    queryset = Envoyer_Message.objects.all()
    serializer_class = EnvoyerMessageSerializer


class Inbox(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    def get(self, request):
        user = request.user
        if user.is_anonymous:
            return Response({'error': 'User not logged in'}, status=status.HTTP_401_UNAUTHORIZED)

        # Filter received messages for the logged-in user
        received_messages = Recevoir_Message.objects.filter(user=user)
        serializer = RecevoirMessageSerializer(received_messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        if user.is_anonymous:
            return Response({'error': 'User not logged in'}, status=status.HTTP_401_UNAUTHORIZED)

        selected_messages = request.data.get('selected_messages', [])
        categorie = request.data.get('categorie')
        if not selected_messages or not categorie:
            return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            categorie_gmail = Categorie_Gmail.objects.get(Contenu=categorie)
        except Categorie_Gmail.DoesNotExist:
            return Response({'error': 'Category does not exist'}, status=status.HTTP_404_NOT_FOUND)

        for message_id in selected_messages:
            try:
                message = Gmail_Message.objects.get(id=message_id)
                message.categorie = categorie_gmail
                message.save()
            except Gmail_Message.DoesNotExist:
                logger.error(f"Message with id {message_id} does not exist.")
        
        return Response({'message': f'Messages marked as {categorie}.'}, status=status.HTTP_200_OK)

class SendEmail(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    def post(self, request):
        user = request.user
        if user.is_anonymous:
            return Response({'error': 'User not logged in'}, status=status.HTTP_401_UNAUTHORIZED)

        recipient_email = request.data.get('recipient')
        content = request.data.get('content')

        cleaned_content = clean_text(content)
        message_tfidf = loaded_vectorizer_rf.transform([cleaned_content])
        prediction = loaded_model_rf.predict(message_tfidf)[0]

        categorie = Categorie_Gmail.objects.get_or_create(Contenu=prediction)[0]

        try:
            recipient = AppUser.objects.get(email=recipient_email)
            # Créer le message en assignant l'utilisateur directement avec l'ID résolu
            message = Gmail_Message.objects.create(
                Contenu=content, 
                date=timezone.now(), 
                categorie=categorie
            )
            # Associer le message envoyé à l'utilisateur
            Envoyer_Message.objects.create(user_id=user.user_id, message=message)
            # Associer le message reçu au destinataire
            Recevoir_Message.objects.create(user_id=recipient.user_id, message=message)

            return Response({'message': 'Email sent successfully.'}, status=status.HTTP_201_CREATED)
        except AppUser.DoesNotExist:
            return Response({'error': 'Recipient not found.'}, status=status.HTTP_404_NOT_FOUND)


class RetrainModel(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    def post(self, request):
        original_data = pd.read_csv('sample_data/email_traduit.csv')
        original_data['Message Traduit'] = original_data['Message Traduit'].apply(clean_text)
        original_data.dropna(subset=['Category', 'Message Traduit'], inplace=True)

        df_original = original_data[['Category', 'Message Traduit']]

        messages_data = Gmail_Message.objects.all().values('Contenu', 'categorie')
        df_gmail = pd.DataFrame(list(messages_data))
        df_gmail.dropna(subset=['categorie', 'Contenu'], inplace=True)

        combined_df = pd.concat([
            df_gmail.rename(columns={'categorie': 'Category', 'Contenu': 'Message Traduit'}),
            df_original
        ], ignore_index=True)

        combined_df['Category'] = combined_df['Category'].astype(str)
        combined_df['Message Traduit'] = combined_df['Message Traduit'].astype(str)
        combined_df.dropna(subset=['Category', 'Message Traduit'], inplace=True)

        X_train, X_test, y_train, y_test = train_test_split(
            combined_df['Message Traduit'], combined_df['Category'], test_size=0.2, random_state=42
        )

        vectorizer = TfidfVectorizer()
        X_train_vec = vectorizer.fit_transform(X_train)
        X_test_vec = vectorizer.transform(X_test)

        clf_lr = LogisticRegression(random_state=42)
        clf_lr.fit(X_train_vec, y_train)

        y_pred_lr = clf_lr.predict(X_test_vec)
        accuracy = accuracy_score(y_test, y_pred_lr)
        print("Accuracy (Logistic Regression):", accuracy)
        print("Classification Report (Logistic Regression):\n", classification_report(y_test, y_pred_lr))

        joblib.dump(clf_lr, r'sample_data/logistic_regression_model.joblib')
        joblib.dump(vectorizer, r'sample_data/tfidf_vectorizer_regretion.joblib')

        return Response({'message': f'Modèle réentraîné avec succès. Précision: {accuracy:.2f}'}, status=status.HTTP_200_OK)


class FetchCategories(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def get(self, request):
        categories = Categorie_Gmail.objects.all()
        serializer = CategorieGmailSerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
