# AI Petition & Grievance Management System

A full-stack AI-powered platform for managing citizen petitions with automated classification, duplicate detection, and SLA monitoring.

## 🚀 Features

### Core Functionality
- ✅ **AI-Powered Classification**: Automatic department routing using Google Gemini
- ✅ **Urgency Prediction**: AI-based priority assessment (LOW/MEDIUM/HIGH/CRITICAL)
- ✅ **Duplicate Detection**: Vector similarity using ChromaDB and Gemini embeddings
- ✅ **Status Tracking**: Complete workflow from submission to resolution
- ✅ **SLA Monitoring**: Automated reminders and escalations via Celery
- ✅ **Email Notifications**: Status updates sent to citizens
- ✅ **File Uploads**: Support for petition attachments
- ✅ **Role-Based Access**: Citizen, Officer, and Admin portals

### Technology Stack
**Backend:**
- Django 5.2 + Django REST Framework
- Waitress (Production WSGI server)
- Google Gemini AI (gemini-2.0-flash)
- ChromaDB (Vector database)
- Celery + Redis (Background tasks)
- SQLite (Database)

**Frontend:**
- React 19 + TypeScript
- Vite 7 (Build tool)
- TailwindCSS 3 (Styling)
- Redux Toolkit (State management)
- React Router DOM (Navigation)

## 📋 Prerequisites

- Python 3.12+
- Node.js 18+
- Redis (for Celery)
- Google Gemini API Key

## 🛠️ Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd AIPetition
```

### 2. Backend Setup
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build
```

## 🚀 Running the Application

### Development Mode

**Terminal 1 - Backend:**
```bash
cd backend
python run_waitress.py
```
Server runs on: `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Dev server runs on: `http://localhost:5173`

**Terminal 3 - Celery Worker (Optional):**
```bash
cd backend
celery -A config worker -l info
```

**Terminal 4 - Celery Beat (Optional):**
```bash
cd backend
celery -A config beat -l info
```

### Production Deployment

1. **Configure Environment Variables:**
```env
GOOGLE_API_KEY=your_gemini_api_key
SECRET_KEY=your_secret_key_here
DEBUG=False
```

2. **Set up Redis:**
```bash
# Install Redis
# Windows: Download from https://redis.io/download
# Linux: sudo apt-get install redis-server
# macOS: brew install redis

# Start Redis
redis-server
```

3. **Configure Email (Optional):**
Edit `backend/config/settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
```

4. **Deploy with Docker (Recommended):**
```bash
docker-compose up -d
```

## 📚 API Documentation

### Authentication
```http
POST /api/users/register/
POST /api/users/login/
POST /api/users/token/refresh/
```

### Petitions
```http
GET    /api/petitions/          # List petitions
POST   /api/petitions/          # Create petition
GET    /api/petitions/{id}/     # Retrieve petition
PATCH  /api/petitions/{id}/     # Update petition
DELETE /api/petitions/{id}/     # Delete petition
```

### Example: Create Petition
```bash
curl -X POST http://localhost:8000/api/petitions/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "title=Broken Street Light" \
  -F "description=Street light broken for 2 weeks" \
  -F "uploaded_files=@photo1.jpg" \
  -F "uploaded_files=@photo2.jpg"
```

## 🧪 Testing

### Run Complete System Test
```bash
cd backend
python test_complete_system.py
```

This tests:
- User registration and authentication
- AI department classification
- AI urgency prediction
- ChromaDB duplicate detection
- Status updates and notifications

## 📁 Project Structure

```
AIPetition/
├── backend/
│   ├── config/              # Django settings
│   ├── users/               # User authentication
│   ├── petitions/           # Petition management
│   ├── ai_agent/            # AI services
│   │   ├── services.py      # Gemini classification
│   │   └── duplicate_detection.py  # ChromaDB
│   ├── run_waitress.py      # Production server
│   └── manage.py
├── frontend/
│   ├── src/
│   │   ├── pages/           # React pages
│   │   ├── components/      # Reusable components
│   │   ├── store/           # Redux store
│   │   └── services/        # API client
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## 🔑 Key Features Explained

### AI Classification
Petitions are automatically classified into departments:
- Roads & Transport
- Electricity
- Water Supply
- Sanitation
- Police
- Health
- Education
- General

### Duplicate Detection
Uses vector embeddings to detect similar petitions:
1. Generate embedding for new petition
2. Query ChromaDB for similar petitions
3. Flag if similarity > 85%

### SLA Monitoring
Celery Beat runs hourly to check:
- SLA violations (overdue petitions)
- SLA warnings (< 2 hours remaining)
- Sends email notifications to officers

### Notifications
- **Status Updates**: Email sent to citizen when status changes
- **SLA Alerts**: Email sent to officers for violations
- **Console Backend**: Development mode logs emails to console

## 🐛 Troubleshooting

### Gemini API Errors
- Ensure `GOOGLE_API_KEY` is set in `.env`
- Check API quota at https://console.cloud.google.com
- Verify model name is correct (`gemini-2.0-flash`)

### ChromaDB Issues
- ChromaDB data stored in `backend/chroma_data/`
- Delete directory to reset: `rm -rf chroma_data/`

### Celery Not Running
- Ensure Redis is running: `redis-cli ping` should return `PONG`
- Check Celery logs for errors
- Verify `CELERY_BROKER_URL` in settings

## 📝 License

MIT License

## 👥 Contributors

- AI Petition Team

## 🙏 Acknowledgments

- Google Gemini AI
- ChromaDB
- Django & React communities
