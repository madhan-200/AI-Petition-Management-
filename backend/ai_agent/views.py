from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ai_agent.chatbot import get_chatbot_response, get_petition_help

class ChatbotView(APIView):
    """
    API endpoint for chatbot interactions.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Handle chatbot message.
        
        Request body:
        {
            "message": "user message",
            "conversation_history": [
                {"role": "user", "content": "previous message"},
                {"role": "assistant", "content": "previous response"}
            ]
        }
        """
        user_message = request.data.get('message', '').strip()
        conversation_history = request.data.get('conversation_history', [])
        
        if not user_message:
            return Response(
                {"error": "Message is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check for quick help commands
        if user_message.lower() in ['help', '/help']:
            response_text = get_petition_help('general')
        elif 'submit' in user_message.lower() and 'how' in user_message.lower():
            response_text = get_petition_help('submit')
        elif 'status' in user_message.lower():
            response_text = get_petition_help('status')
        elif 'urgency' in user_message.lower() or 'priority' in user_message.lower():
            response_text = get_petition_help('urgency')
        elif 'department' in user_message.lower():
            response_text = get_petition_help('departments')
        else:
            # Get AI response
            response_text = get_chatbot_response(user_message, conversation_history)
        
        return Response({
            "response": response_text,
            "timestamp": request.data.get('timestamp')
        })

class ChatbotHelpView(APIView):
    """
    Get help information for specific topics.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get help for a specific topic."""
        topic = request.query_params.get('topic', 'general')
        help_text = get_petition_help(topic)
        
        return Response({
            "topic": topic,
            "help": help_text
        })
