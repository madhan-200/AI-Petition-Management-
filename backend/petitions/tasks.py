from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from petitions.models import Petition, SLA

@shared_task
def check_sla_violations():
    """
    Periodic task to check for SLA violations and send reminders.
    Run this task every hour via Celery Beat.
    """
    pending_statuses = ['SUBMITTED', 'UNDER_REVIEW', 'ASSIGNED', 'IN_PROGRESS']
    pending_petitions = Petition.objects.filter(status__in=pending_statuses)
    
    violations = []
    
    for petition in pending_petitions:
        if not petition.department:
            continue
        
        # Get SLA for this petition's department and urgency
        try:
            sla = SLA.objects.get(department=petition.department, urgency=petition.urgency)
            resolution_deadline = petition.created_at + timedelta(hours=sla.resolution_time_hours)
            
            # Check if SLA is violated or about to be violated (within 2 hours)
            time_remaining = resolution_deadline - timezone.now()
            
            if time_remaining.total_seconds() < 0:
                # SLA violated
                violations.append({
                    'petition': petition,
                    'status': 'VIOLATED',
                    'hours_overdue': abs(time_remaining.total_seconds() / 3600)
                })
            elif time_remaining.total_seconds() < 7200:  # Less than 2 hours remaining
                # SLA warning
                violations.append({
                    'petition': petition,
                    'status': 'WARNING',
                    'hours_remaining': time_remaining.total_seconds() / 3600
                })
        except SLA.DoesNotExist:
            continue
    
    # Send notifications for violations
    for violation in violations:
        send_sla_notification.delay(
            petition_id=violation['petition'].id,
            status=violation['status']
        )
    
    return f"Checked {pending_petitions.count()} petitions, found {len(violations)} SLA issues"

@shared_task
def send_sla_notification(petition_id, status):
    """Send email notification for SLA violation or warning."""
    try:
        petition = Petition.objects.get(id=petition_id)
        
        subject = f"SLA {status}: Petition #{petition.id}"
        
        if status == 'VIOLATED':
            message = f"""
SLA Violation Alert

Petition ID: {petition.id}
Title: {petition.title}
Department: {petition.department.name if petition.department else 'N/A'}
Urgency: {petition.urgency}
Status: {petition.status}
Created: {petition.created_at}

This petition has exceeded its SLA resolution time. Immediate action required.
            """
        else:
            message = f"""
SLA Warning

Petition ID: {petition.id}
Title: {petition.title}
Department: {petition.department.name if petition.department else 'N/A'}
Urgency: {petition.urgency}
Status: {petition.status}
Created: {petition.created_at}

This petition's SLA deadline is approaching (less than 2 hours remaining).
            """
        
        # Send to admin/officer email
        # In production, get officer email from petition.department
        recipient_email = settings.DEFAULT_FROM_EMAIL  # Fallback
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
        )
        
        return f"Sent {status} notification for petition {petition_id}"
    except Petition.DoesNotExist:
        return f"Petition {petition_id} not found"
    except Exception as e:
        return f"Failed to send notification: {str(e)}"

@shared_task
def send_status_update_notification(petition_id):
    """Send email to citizen when petition status is updated."""
    try:
        petition = Petition.objects.get(id=petition_id)
        
        subject = f"Petition #{petition.id} Status Update"
        message = f"""
Dear {petition.citizen.username},

Your petition has been updated:

Title: {petition.title}
Current Status: {petition.status}
Department: {petition.department.name if petition.department else 'Pending'}
Urgency: {petition.urgency}

You can track your petition status at: http://localhost:5173/dashboard

Thank you for using our service.
        """
        
        # Send to citizen email
        if petition.citizen.email:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [petition.citizen.email],
                fail_silently=False,
            )
            return f"Sent status update to {petition.citizen.email}"
        else:
            return f"No email found for citizen {petition.citizen.username}"
    except Petition.DoesNotExist:
        return f"Petition {petition_id} not found"
    except Exception as e:
        return f"Failed to send notification: {str(e)}"
