from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer
from .mongo_repository import UserRepository
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint - stores in both Django ORM and MongoDB.
    """
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create user in Django ORM (for authentication)
        user = serializer.save()
        
        # Also create in MongoDB
        try:
            mongo_user = UserRepository.create_user(
                username=user.username,
                email=user.email,
                password=request.data.get('password'),  # Plain password for MongoDB hashing
                role=user.role
            )
            
            if mongo_user:
                logger.info(f"✅ User synced to MongoDB: {user.username}")
            else:
                logger.warning(f"⚠️ User created in Django but MongoDB sync failed: {user.username}")
                
        except Exception as e:
            logger.error(f"MongoDB sync error: {e}")
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
