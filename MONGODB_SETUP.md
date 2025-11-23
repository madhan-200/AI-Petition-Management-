# MongoDB Integration Guide

## Overview
This guide explains how to migrate from SQLite to MongoDB for the AI Petition System.

## Prerequisites
- MongoDB installed locally OR MongoDB Atlas account
- Python packages: `pymongo`, `djongo`

## Option 1: Local MongoDB

### 1. Install MongoDB
**Windows:**
```bash
# Download from https://www.mongodb.com/try/download/community
# Install and start MongoDB service
```

**Linux:**
```bash
sudo apt-get install mongodb
sudo systemctl start mongodb
```

**macOS:**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

### 2. Update Django Settings
Edit `backend/config/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'ai_petition_db',
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': 'localhost',
            'port': 27017,
        }
    }
}
```

## Option 2: MongoDB Atlas (Cloud)

### 1. Create MongoDB Atlas Account
1. Go to https://www.mongodb.com/cloud/atlas
2. Create a free cluster
3. Create a database user
4. Whitelist your IP address
5. Get connection string

### 2. Update Django Settings
```python
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'ai_petition_db',
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': 'mongodb+srv://username:password@cluster.mongodb.net/ai_petition_db?retryWrites=true&w=majority'
        }
    }
}
```

### 3. Add to .env
```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/ai_petition_db?retryWrites=true&w=majority
```

## Migration Steps

### 1. Backup SQLite Data
```bash
cd backend
python manage.py dumpdata > backup.json
```

### 2. Update Settings
Choose Option 1 or Option 2 above and update `settings.py`

### 3. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Load Data (Optional)
```bash
python manage.py loaddata backup.json
```

## Verification

### Test MongoDB Connection
```bash
python manage.py shell
```

```python
from django.db import connection
connection.ensure_connection()
print("MongoDB connected successfully!")
```

### Test API
```bash
python test_complete_system.py
```

## Troubleshooting

### Error: "No module named 'djongo'"
```bash
pip install djongo pymongo
```

### Error: "Connection refused"
- Ensure MongoDB is running: `sudo systemctl status mongodb`
- Check firewall settings
- Verify connection string

### Error: "Authentication failed"
- Check username/password in connection string
- Verify database user permissions in MongoDB Atlas

## Performance Optimization

### Create Indexes
```python
# In Django shell
from petitions.models import Petition
from django.db import connection

# Create indexes for frequently queried fields
collection = connection.get_collection('petitions_petition')
collection.create_index('status')
collection.create_index('urgency')
collection.create_index('citizen_id')
collection.create_index('created_at')
```

## Rollback to SQLite

If you need to rollback:

1. Restore `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

2. Run migrations:
```bash
python manage.py migrate
```

3. Load backup:
```bash
python manage.py loaddata backup.json
```

## Notes

- **djongo** is a connector that allows Django ORM to work with MongoDB
- MongoDB is schema-less, but Django models still define structure
- File uploads (attachments) work the same way with MongoDB
- ChromaDB remains separate and unaffected by this change

## Production Recommendations

1. Use MongoDB Atlas for production (managed service)
2. Enable authentication
3. Use connection pooling
4. Set up replica sets for high availability
5. Configure backups
6. Monitor performance with MongoDB Atlas monitoring tools
