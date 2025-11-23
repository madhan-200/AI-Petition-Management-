from django.db import models
from django.conf import settings

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class SLA(models.Model):
    class Urgency(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        CRITICAL = 'CRITICAL', 'Critical'

    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='slas')
    urgency = models.CharField(max_length=20, choices=Urgency.choices)
    resolution_time_hours = models.IntegerField(help_text="Time in hours to resolve")

    class Meta:
        unique_together = ('department', 'urgency')

    def __str__(self):
        return f"{self.department.name} - {self.urgency} ({self.resolution_time_hours}h)"

class Petition(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = 'SUBMITTED', 'Submitted'
        UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
        ASSIGNED = 'ASSIGNED', 'Assigned'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        RESOLVED = 'RESOLVED', 'Resolved'
        REJECTED = 'REJECTED', 'Rejected'
        CLOSED = 'CLOSED', 'Closed'

    title = models.CharField(max_length=200)
    description = models.TextField()
    citizen = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='petitions')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='petitions')
    assigned_officer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_petitions',
        limit_choices_to={'role': 'OFFICER'}
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)
    urgency = models.CharField(max_length=20, choices=SLA.Urgency.choices, default=SLA.Urgency.LOW)
    is_duplicate = models.BooleanField(default=False, help_text="Flagged as potential duplicate")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.status})"

class Attachment(models.Model):
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.petition.id}"

class ResolutionDocument(models.Model):
    """Documents uploaded by officers as proof of resolution"""
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE, related_name='resolution_documents')
    file = models.FileField(upload_to='resolutions/')
    description = models.TextField(blank=True, help_text="Description of the resolution document")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resolution for Petition #{self.petition.id}"

class AuditLog(models.Model):
    """Track all actions performed on petitions"""
    class Action(models.TextChoices):
        CREATED = 'CREATED', 'Created'
        STATUS_CHANGED = 'STATUS_CHANGED', 'Status Changed'
        ASSIGNED = 'ASSIGNED', 'Assigned to Officer'
        DOCUMENT_UPLOADED = 'DOCUMENT_UPLOADED', 'Document Uploaded'
        UPDATED = 'UPDATED', 'Updated'
    
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE, related_name='audit_logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50, choices=Action.choices)
    old_value = models.TextField(blank=True, help_text="Previous value (for changes)")
    new_value = models.TextField(blank=True, help_text="New value (for changes)")
    remarks = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} on Petition #{self.petition.id} by {self.user}"
