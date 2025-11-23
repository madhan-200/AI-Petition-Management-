from rest_framework import serializers
from .models import Petition, Attachment, Department, SLA

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ('id', 'file', 'uploaded_at')

class PetitionSerializer(serializers.ModelSerializer):
    citizen_username = serializers.CharField(source='citizen.username', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    uploaded_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Petition
        fields = ['id', 'title', 'description', 'status', 'urgency', 'is_duplicate',
                  'department_name', 'citizen_username', 'created_at', 'updated_at', 
                  'attachments', 'uploaded_files']
        read_only_fields = ['id', 'status', 'urgency', 'is_duplicate', 'created_at', 'updated_at']
