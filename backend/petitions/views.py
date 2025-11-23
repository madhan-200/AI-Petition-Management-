from rest_framework import viewsets, permissions, parsers, status
from rest_framework.response import Response
from .models import Petition, Attachment, Department, SLA
from .serializers import PetitionSerializer, AttachmentSerializer
from .mongo_repository import PetitionRepository
from ai_agent.services import classify_department, predict_urgency
from ai_agent.duplicate_detection import check_duplicate, add_petition_to_index
import logging

logger = logging.getLogger(__name__)

class PetitionViewSet(viewsets.ModelViewSet):
    queryset = Petition.objects.all().order_by('-created_at')
    serializer_class = PetitionSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def perform_create(self, serializer):
        title = serializer.validated_data.get('title', '')
        description = serializer.validated_data.get('description', '')
        
        # Get uploaded files from request
        uploaded_files = self.request.FILES.getlist('uploaded_files')
        
        # Check for duplicates
        duplicate_check = check_duplicate(title, description)
        
        # AI Processing
        dept_name = classify_department(title, description)
        urgency = predict_urgency(title, description)
        
        department, _ = Department.objects.get_or_create(name=dept_name)
        
        # Save petition in Django ORM
        petition = serializer.save(
            citizen=self.request.user, 
            department=department, 
            urgency=urgency,
            is_duplicate=duplicate_check['is_duplicate']
        )
        
        # Save attachments
        attachment_paths = []
        for file in uploaded_files:
            att = Attachment.objects.create(petition=petition, file=file)
            attachment_paths.append(str(att.file.url))
        
        # Also save in MongoDB
        try:
            mongo_petition = PetitionRepository.create_petition({
                'title': title,
                'description': description,
                'citizen_id': str(self.request.user.id),
                'citizen_username': self.request.user.username,
                'department': dept_name,
                'status': petition.status,
                'urgency': urgency,
                'is_duplicate': duplicate_check['is_duplicate'],
                'attachments': attachment_paths
            })
            
            if mongo_petition:
                logger.info(f"✅ Petition synced to MongoDB: {petition.id}")
            else:
                logger.warning(f"⚠️ Petition created in Django but MongoDB sync failed: {petition.id}")
                
        except Exception as e:
            logger.error(f"MongoDB sync error: {e}")
        
        # Add to ChromaDB index for future duplicate detection
        add_petition_to_index(petition.id, title, description)

    def get_queryset(self):
        user = self.request.user
        if user.role == 'CITIZEN':
            return Petition.objects.filter(citizen=user)
        elif user.role == 'OFFICER':
            # TODO: Filter by officer's department
            return Petition.objects.all()
        return Petition.objects.all()
    
    def perform_update(self, serializer):
        """Trigger notification when petition status is updated."""
        old_status = self.get_object().status
        petition = serializer.save()
        new_status = petition.status
        
        # Sync update to MongoDB
        try:
            PetitionRepository.update_petition(
                str(petition.id),
                {
                    'status': new_status,
                    'urgency': petition.urgency
                }
            )
            logger.info(f"✅ Petition update synced to MongoDB: {petition.id}")
        except Exception as e:
            logger.error(f"MongoDB sync error: {e}")
        
        # Send notification if status changed
        if old_status != new_status:
            from petitions.tasks import send_status_update_notification
            send_status_update_notification.delay(petition.id)
