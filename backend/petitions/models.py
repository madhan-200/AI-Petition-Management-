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
