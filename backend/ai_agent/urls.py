from django.urls import path
from .views import ChatbotView, ChatbotHelpView

urlpatterns = [
    path('chat/', ChatbotView.as_view(), name='chatbot'),
    path('chat/help/', ChatbotHelpView.as_view(), name='chatbot-help'),
]
