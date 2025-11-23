"""
Audit Logging Utilities

Track all actions performed on petitions for compliance and transparency.
"""

from petitions.models import AuditLog
import logging

logger = logging.getLogger(__name__)

def log_action(petition, user, action, old_value="", new_value="", remarks=""):
    """
    Create an audit log entry.
    
    Args:
        petition: Petition instance
        user: User who performed the action
        action: Action type (from AuditLog.Action choices)
        old_value: Previous value (for changes)
        new_value: New value (for changes)
        remarks: Additional notes
    
    Returns:
        AuditLog instance
    """
    try:
        audit_entry = AuditLog.objects.create(
            petition=petition,
            user=user,
            action=action,
            old_value=str(old_value),
            new_value=str(new_value),
            remarks=remarks
        )
        
        logger.info(f"📝 Audit log created: {action} on Petition #{petition.id} by {user.username}")
        return audit_entry
        
    except Exception as e:
        logger.error(f"Failed to create audit log: {e}")
        return None

def log_petition_created(petition, user):
    """Log petition creation."""
    return log_action(
        petition=petition,
        user=user,
        action=AuditLog.Action.CREATED,
        new_value=f"Title: {petition.title}, Department: {petition.department}, Urgency: {petition.urgency}",
        remarks="Petition submitted by citizen"
    )

def log_status_change(petition, user, old_status, new_status, remarks=""):
    """Log status change."""
    return log_action(
        petition=petition,
        user=user,
        action=AuditLog.Action.STATUS_CHANGED,
        old_value=old_status,
        new_value=new_status,
        remarks=remarks
    )

def log_officer_assigned(petition, user, officer):
    """Log officer assignment."""
    return log_action(
        petition=petition,
        user=user,
        action=AuditLog.Action.ASSIGNED,
        new_value=f"Assigned to: {officer.username} ({officer.email})",
        remarks="Auto-assigned based on department and workload"
    )

def log_document_upload(petition, user, document_type, filename):
    """Log document upload."""
    return log_action(
        petition=petition,
        user=user,
        action=AuditLog.Action.DOCUMENT_UPLOADED,
        new_value=f"{document_type}: {filename}",
        remarks=f"Document uploaded by {user.role}"
    )

def get_petition_audit_trail(petition):
    """Get complete audit trail for a petition."""
    return AuditLog.objects.filter(petition=petition).select_related('user')
