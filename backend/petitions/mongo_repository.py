"""
MongoDB Repository for Petitions

Handles Petition data storage and retrieval in MongoDB.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from config.mongodb import get_collection
import logging

logger = logging.getLogger(__name__)

class PetitionRepository:
    """Repository for Petition operations in MongoDB."""
    
    COLLECTION_NAME = 'petitions'
    
    @staticmethod
    def _get_collection():
        """Get petitions collection."""
        return get_collection(PetitionRepository.COLLECTION_NAME)
    
    @staticmethod
    def create_petition(data: Dict) -> Optional[Dict]:
        """
        Create a new petition in MongoDB.
        
        Args:
            data: Petition data including title, description, citizen_id, etc.
        
        Returns:
            Created petition document or None
        """
        collection = PetitionRepository._get_collection()
        if collection is None:
            logger.error("MongoDB collection not available")
            return None
        
        try:
            petition_doc = {
                'title': data.get('title'),
                'description': data.get('description'),
                'citizen_id': data.get('citizen_id'),
                'citizen_username': data.get('citizen_username'),
                'department': data.get('department', 'General'),
                'status': data.get('status', 'SUBMITTED'),
                'urgency': data.get('urgency', 'LOW'),
                'is_duplicate': data.get('is_duplicate', False),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'attachments': data.get('attachments', []),
                'remarks': []
            }
            
            result = collection.insert_one(petition_doc)
            petition_doc['_id'] = result.inserted_id
            
            logger.info(f"✅ Petition created in MongoDB: {petition_doc['_id']}")
            return petition_doc
            
        except Exception as e:
            logger.error(f"Failed to create petition: {e}")
            return None
    
    @staticmethod
    def get_petition_by_id(petition_id: str) -> Optional[Dict]:
        """Get petition by MongoDB ObjectId."""
        collection = PetitionRepository._get_collection()
        if collection is None:
            return None
        
        try:
            return collection.find_one({'_id': ObjectId(petition_id)})
        except:
            return None
    
    @staticmethod
    def get_petitions_by_citizen(citizen_id: str) -> List[Dict]:
        """Get all petitions for a specific citizen."""
        collection = PetitionRepository._get_collection()
        if collection is None:
            return []
        
        return list(collection.find({'citizen_id': citizen_id}).sort('created_at', -1))
    
    @staticmethod
    def get_all_petitions(filters: Optional[Dict] = None) -> List[Dict]:
        """
        Get all petitions with optional filters.
        
        Args:
            filters: MongoDB query filters (e.g., {'status': 'SUBMITTED'})
        
        Returns:
            List of petition documents
        """
        collection = PetitionRepository._get_collection()
        if collection is None:
            return []
        
        query = filters if filters else {}
        return list(collection.find(query).sort('created_at', -1))
    
    @staticmethod
    def update_petition(petition_id: str, updates: Dict) -> bool:
        """
        Update petition document.
        
        Args:
            petition_id: MongoDB ObjectId as string
            updates: Dictionary of fields to update
        
        Returns:
            True if updated successfully
        """
        collection = PetitionRepository._get_collection()
        if collection is None:
            return False
        
        try:
            updates['updated_at'] = datetime.utcnow()
            
            result = collection.update_one(
                {'_id': ObjectId(petition_id)},
                {'$set': updates}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update petition: {e}")
            return False
    
    @staticmethod
    def add_remark(petition_id: str, remark: Dict) -> bool:
        """Add a remark to petition."""
        collection = PetitionRepository._get_collection()
        if collection is None:
            return False
        
        try:
            remark['timestamp'] = datetime.utcnow()
            
            result = collection.update_one(
                {'_id': ObjectId(petition_id)},
                {
                    '$push': {'remarks': remark},
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to add remark: {e}")
            return False
    
    @staticmethod
    def delete_petition(petition_id: str) -> bool:
        """Delete petition from MongoDB."""
        collection = PetitionRepository._get_collection()
        if collection is None:
            return False
        
        try:
            result = collection.delete_one({'_id': ObjectId(petition_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to delete petition: {e}")
            return False
    
    @staticmethod
    def get_statistics() -> Dict:
        """Get petition statistics."""
        collection = PetitionRepository._get_collection()
        if collection is None:
            return {}
        
        try:
            total = collection.count_documents({})
            pending = collection.count_documents({'status': {'$in': ['SUBMITTED', 'UNDER_REVIEW', 'ASSIGNED', 'IN_PROGRESS']}})
            resolved = collection.count_documents({'status': 'RESOLVED'})
            critical = collection.count_documents({'urgency': 'CRITICAL'})
            
            return {
                'total': total,
                'pending': pending,
                'resolved': resolved,
                'critical': critical
            }
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
