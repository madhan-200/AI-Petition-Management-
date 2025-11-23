"""
Auto-Assignment Logic for Petitions

Automatically assigns petitions to officers based on:
- Department match
- Officer availability
- Workload balancing (least-load algorithm)
"""

from django.contrib.auth import get_user_model
from petitions.models import Petition
from django.db.models import Count
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

def assign_to_officer(petition):
    """
    Automatically assign petition to an available officer.
    
    Algorithm:
    1. Find officers in the petition's department
    2. Filter for active officers
    3. Calculate current workload (pending petitions)
    4. Assign to officer with least workload
    
    Args:
        petition: Petition instance
    
    Returns:
        User instance (officer) or None
    """
    if not petition.department:
        logger.warning(f"Petition {petition.id} has no department, cannot auto-assign")
        return None
    
    # Find active officers in the department
    officers = User.objects.filter(
        role='OFFICER',
        department=petition.department,
        is_active_officer=True,
        is_active=True
    )
    
    if not officers.exists():
        logger.warning(f"No active officers found for department: {petition.department.name}")
        return None
    
    # Calculate workload for each officer (count of pending petitions)
    officers_with_workload = officers.annotate(
        pending_count=Count(
            'assigned_petitions',
            filter=models.Q(
                assigned_petitions__status__in=[
                    'SUBMITTED', 'UNDER_REVIEW', 'ASSIGNED', 'IN_PROGRESS'
                ]
            )
        )
    ).order_by('pending_count')
    
    # Assign to officer with least workload
    selected_officer = officers_with_workload.first()
    
    if selected_officer:
        petition.assigned_officer = selected_officer
        petition.status = 'ASSIGNED'
        petition.save()
        
        logger.info(
            f"✅ Petition {petition.id} auto-assigned to {selected_officer.username} "
            f"(current workload: {selected_officer.pending_count} petitions)"
        )
        
        return selected_officer
    
    return None

def get_officer_workload(officer):
    """Get current workload for an officer."""
    if officer.role != 'OFFICER':
        return 0
    
    return Petition.objects.filter(
        assigned_officer=officer,
        status__in=['SUBMITTED', 'UNDER_REVIEW', 'ASSIGNED', 'IN_PROGRESS']
    ).count()

def get_department_officers(department):
    """Get all active officers in a department."""
    return User.objects.filter(
        role='OFFICER',
        department=department,
        is_active_officer=True,
        is_active=True
    )
