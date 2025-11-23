from rest_framework import viewsets, permissions, parsers, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Petition, Attachment, Department, SLA, ResolutionDocument
from .serializers import PetitionSerializer, AttachmentSerializer, ResolutionDocumentSerializer, AuditLogSerializer
from .mongo_repository import PetitionRepository
from .assignment import assign_to_officer
from .audit import log_petition_created, log_status_change, log_officer_assigned, log_document_upload, get_petition_audit_trail
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
        
        # Auto-assign to officer
        assigned_officer = assign_to_officer(petition)
        if assigned_officer:
            log_officer_assigned(petition, self.request.user, assigned_officer)
        
        # Audit log: Petition created
        log_petition_created(petition, self.request.user)
        
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
    
    @action(detail=True, methods=['post'], parser_classes=[parsers.MultiPartParser])
    def upload_resolution(self, request, pk=None):
        """Upload resolution document for a petition."""
        petition = self.get_object()
        file = request.FILES.get('file')
        description = request.data.get('description', '')
        
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create resolution document
        doc = ResolutionDocument.objects.create(
            petition=petition,
            file=file,
            description=description,
            uploaded_by=request.user
        )
        
        # Log the upload
        log_document_upload(petition, request.user, 'Resolution', file.name)
        
        serializer = ResolutionDocumentSerializer(doc)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def audit_log(self, request, pk=None):
        """Get audit trail for a petition."""
        petition = self.get_object()
        logs = get_petition_audit_trail(petition)
        serializer = AuditLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    def perform_update(self, serializer):
        """Trigger notification when petition status is updated."""
        old_status = self.get_object().status
        petition = serializer.save()
        new_status = petition.status
        
        # Audit log: Status change
        if old_status != new_status:
            remarks = serializer.validated_data.get('remarks', '')
            log_status_change(petition, self.request.user, old_status, new_status, remarks)
        
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
