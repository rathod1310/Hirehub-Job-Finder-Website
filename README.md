# HireHub - Job Finder Website

HireHub is a Django based job portal for companies and applicants. Companies can post jobs, manage applications, and track hiring activity from a dashboard. Applicants can browse jobs, apply with a CV, and track their application status.

## Features

### Company Side

- Company registration and login
- Company dashboard with hiring analytics
- Post jobs manually
- Bulk upload jobs using CSV or Excel
- Edit and delete posted jobs
- View all posted jobs
- View all applicants for company jobs
- Open applicant detail page with full application data and CV
- Update applicant status:
  - Applied
  - Under Review
  - Shortlisted
  - Rejected
- Email notification to applicant when status changes
- Export applied applicant data to CSV
- Logout functionality

### Applicant Side

- Applicant registration and login
- Email notification after successful registration
- Update profile
- Browse available jobs
- Search jobs
- Apply for jobs with CV/resume upload
- Email notification to applicant after applying
- Email notification to company when an applicant applies
- View applied jobs and current application status
- Logout functionality

## Built With

- Python
- Django
- SQLite
- HTML
- CSS
- JavaScript
- Bootstrap

## Setup

1. Create and activate a virtual environment.

```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Run migrations.

```bash
python manage.py migrate
```

4. Start the development server.

```bash
python manage.py runserver
```

5. Open the project in browser.

```text
http://127.0.0.1:8000/
```

## Email Configuration

Email notifications use Gmail SMTP. Update `hirehub/settings.py` with your Gmail address and app password.

```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "your_email@gmail.com"
EMAIL_HOST_PASSWORD = "your_app_password"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

Use a Gmail app password, not your normal Gmail password.

## Media Files

Applicant CV files are stored in the `resumes/` folder and served in development through `/media/resumes/...`.

## Developed By

Om Rathod
