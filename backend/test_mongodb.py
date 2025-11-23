"""
MongoDB Test Script

Tests MongoDB connection and CRUD operations.
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from config.mongodb import get_mongo_db, get_collection
from users.mongo_repository import UserRepository
from petitions.mongo_repository import PetitionRepository

def test_mongodb_connection():
    """Test MongoDB connection."""
    print("\n" + "="*60)
    print("MONGODB CONNECTION TEST")
    print("="*60)
    
    db = get_mongo_db()
    if db is not None:
        print(f"✅ Connected to MongoDB: {db.name}")
        print(f"   Collections: {db.list_collection_names()}")
        return True
    else:
        print("❌ MongoDB connection failed")
        return False

def test_user_operations():
    """Test User CRUD operations."""
    print("\n" + "="*60)
    print("USER OPERATIONS TEST")
    print("="*60)
    
    # Create user
    print("\n1. Creating test user...")
    user = UserRepository.create_user(
        username="mongo_test_user",
        email="test@mongo.com",
        password="testpass123",
        role="CITIZEN"
    )
    
    if user:
        print(f"✅ User created: {user['username']} (ID: {user['_id']})")
    else:
        print("⚠️  User already exists or creation failed")
    
    # Get user
    print("\n2. Retrieving user...")
    user = UserRepository.get_user_by_username("mongo_test_user")
    if user:
        print(f"✅ User retrieved: {user['username']}")
        print(f"   Email: {user['email']}")
        print(f"   Role: {user['role']}")
    
    # Authenticate
    print("\n3. Testing authentication...")
    auth_user = UserRepository.authenticate("mongo_test_user", "testpass123")
    if auth_user:
        print(f"✅ Authentication successful")
    else:
        print("❌ Authentication failed")
    
    # Get all users
    print("\n4. Getting all users...")
    users = UserRepository.get_all_users()
    print(f"✅ Total users in MongoDB: {len(users)}")

def test_petition_operations():
    """Test Petition CRUD operations."""
    print("\n" + "="*60)
    print("PETITION OPERATIONS TEST")
    print("="*60)
    
    # Create petition
    print("\n1. Creating test petition...")
    petition = PetitionRepository.create_petition({
        'title': 'MongoDB Test Petition',
        'description': 'This is a test petition stored in MongoDB',
        'citizen_id': '12345',
        'citizen_username': 'mongo_test_user',
        'department': 'General',
        'status': 'SUBMITTED',
        'urgency': 'MEDIUM'
    })
    
    if petition:
        print(f"✅ Petition created: {petition['title']} (ID: {petition['_id']})")
        petition_id = str(petition['_id'])
    else:
        print("❌ Petition creation failed")
        return
    
    # Get petition
    print("\n2. Retrieving petition...")
    petition = PetitionRepository.get_petition_by_id(petition_id)
    if petition:
        print(f"✅ Petition retrieved: {petition['title']}")
        print(f"   Status: {petition['status']}")
        print(f"   Urgency: {petition['urgency']}")
    
    # Update petition
    print("\n3. Updating petition status...")
    updated = PetitionRepository.update_petition(petition_id, {
        'status': 'UNDER_REVIEW'
    })
    if updated:
        print(f"✅ Petition updated successfully")
        petition = PetitionRepository.get_petition_by_id(petition_id)
        print(f"   New status: {petition['status']}")
    
    # Add remark
    print("\n4. Adding remark...")
    remark_added = PetitionRepository.add_remark(petition_id, {
        'text': 'This is a test remark',
        'author': 'Test Officer'
    })
    if remark_added:
        print(f"✅ Remark added successfully")
    
    # Get statistics
    print("\n5. Getting petition statistics...")
    stats = PetitionRepository.get_statistics()
    print(f"✅ Statistics:")
    print(f"   Total: {stats.get('total', 0)}")
    print(f"   Pending: {stats.get('pending', 0)}")
    print(f"   Resolved: {stats.get('resolved', 0)}")
    print(f"   Critical: {stats.get('critical', 0)}")

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("MONGODB HYBRID INTEGRATION TEST")
    print("="*60)
    
    if not test_mongodb_connection():
        print("\n❌ MongoDB not available. Please ensure MongoDB is running on localhost:27017")
        return
    
    test_user_operations()
    test_petition_operations()
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED")
    print("="*60)
    print("\n💡 Check MongoDB Compass to see the data:")
    print("   Database: regiflow_db")
    print("   Collections: users, petitions")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
