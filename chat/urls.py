from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router for ViewSets
router = DefaultRouter()
router.register(r'gmail-compte', views.GmailCompteViewSet)
router.register(r'gmail-message', views.GmailMessageViewSet)
router.register(r'receive-message', views.RecevoirMessageViewSet)
router.register(r'send-message', views.EnvoyerMessageViewSet)

urlpatterns = [
    path('inbox', views.Inbox.as_view(), name='inbox'),
    path('send-email', views.SendEmail.as_view(), name='send-email'),
    path('retrain-model', views.RetrainModel.as_view(), name='retrain-model'),
    path('categories', views.FetchCategories.as_view(), name='categories'),
    path('', include(router.urls)),
]
