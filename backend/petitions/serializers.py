from rest_framework import serializers
from .models import Petition, Attachment, ResolutionDocument, AuditLog

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file', 'uploaded_at']

class ResolutionDocumentSerializer(serializers.ModelSerializer):
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    
    class Meta:
        model = ResolutionDocument
        fields = ['id', 'file', 'description', 'uploaded_by', 'uploaded_by_username', 'uploaded_at']
        read_only_fields = ['uploaded_by', 'uploaded_at']

class AuditLogSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = ['id', 'action', 'old_value', 'new_value', 'remarks', 'timestamp', 'user_username']

class PetitionSerializer(serializers.ModelSerializer):
    citizen_username = serializers.CharField(source='citizen.username', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    resolution_documents = ResolutionDocumentSerializer(many=True, read_only=True)
    assigned_officer_username = serializers.CharField(source='assigned_officer.username', read_only=True)
    uploaded_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Petition
        fields = [
            'id', 'title', 'description', 'citizen', 'citizen_username',
            'department', 'department_name', 'assigned_officer', 'assigned_officer_username',
            'status', 'urgency', 'is_duplicate', 'created_at', 'updated_at',
            'attachments', 'resolution_documents', 'uploaded_files'
        ]
        read_only_fields = ['citizen', 'department', 'urgency', 'is_duplicate', 'created_at', 'updated_at']
