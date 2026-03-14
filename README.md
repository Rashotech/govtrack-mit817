# GovTrack - Government Projects Transparency Platform

A web-based transparency platform that enables citizens to monitor government infrastructure projects and report community issues. Built with Django and Tailwind CSS.

## Overview

GovTrack provides a public interface for tracking state government infrastructure projects including roads, drainage systems, streetlights, and other public works. Citizens can view project details, financial information, and submit reports about infrastructure issues in their communities.

## Features

- **Project Tracking**: View ongoing, pending, and completed government projects
- **Financial Transparency**: Access budget allocations and disbursement information
- **Citizen Reporting**: Submit and track community infrastructure issues
- **Search & Filter**: Find projects by status, category, location, or contractor
- **Community Engagement**: Upvote citizen reports to prioritize issues
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Tech Stack

- **Backend**: Django 5.0.7
- **Database**: PostgreSQL
- **Storage**: Google Cloud Storage (Firebase)
- **Frontend**: Tailwind CSS
- **Deployment**: Gunicorn + WhiteNoise

## Prerequisites

- Python 3.12+
- PostgreSQL 12+
- pip
- Node.js (for Tailwind CSS)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd DjangoProject
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run database migrations:
```bash
python3 manage.py migrate
```

6. Create admin user:
```bash
python3 manage.py createsuperuser
```

7. Load sample data (optional):
```bash
python3 manage.py seed_data
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
POSTGRES_DB=govtracker
POSTGRES_USER=your-db-user
POSTGRES_PASSWORD=your-db-password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Firebase Storage (optional)
USE_FIREBASE_STORAGE=True
FIREBASE_STORAGE_BUCKET=your-bucket.appspot.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account@project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
```

## Development

### Running the Development Server

Start Tailwind CSS watcher and Django server:
```bash
python3 manage.py tailwind start  # Terminal 1
python3 manage.py runserver       # Terminal 2
```

Or run both together:
```bash
python3 manage.py tailwind dev
```

Access the application at `http://localhost:8000`

### Admin Panel

Access the admin interface at `http://localhost:8000/admin/`


## Production Deployment

1. Set environment variables:
```bash
DEBUG=False
ALLOWED_HOSTS=your-domain.com
```

2. Collect static files:
```bash
python3 manage.py collectstatic --noinput
```

3. Run with Gunicorn:
```bash
gunicorn GovTrack.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

## Project Structure

```
DjangoProject/
├── GovTrack/              # Project settings
├── govtracker/            # Main application
│   ├── models.py          # Database models
│   ├── views.py           # View logic
│   ├── urls.py            # URL routing
│   ├── admin.py           # Admin configuration
│   ├── templatetags/      # Custom template filters
│   └── management/        # Management commands
├── templates/             # HTML templates
│   └── govtracker/
│       ├── base.html
│       ├── home.html
│       └── components/    # Reusable UI components
├── theme/                 # Tailwind CSS configuration
├── staticfiles/           # Collected static files (production)
├── media/                 # User-uploaded files (local)
└── requirements.txt       # Python dependencies
```

## Database Models

- **Project**: Government infrastructure projects
- **ProjectCategory**: Project types (roads, drainage, etc.)
- **ProjectImage**: Project photos and documentation
- **Contractor**: Construction companies
- **LGA**: Local Government Areas
- **CitizenPost**: Community-submitted reports
- **PostMedia**: Images/videos for citizen reports
- **PostUpvote**: Community support tracking

## Routes

- `/` - Homepage
- `/projects/` - All projects listing
- `/projects/<id>/` - Project details
- `/reports/` - Community reports
- `/reports/<reference>/` - Report details
- `/report-issue/` - Submit new report
- `/admin/` - Admin dashboard

## Management Commands

### Seed Database
```bash
python3 manage.py seed_data
```
Creates sample projects, contractors, LGAs, and citizen posts.

---

**Version**: 1.0  
**Last Updated**: March 2026  
**Developed By**: MIT 817 Group 5
