# LoveMatch - Django Dating Website

A comprehensive dating website built with Django framework and beautiful HTML templates. Features include user authentication, profile management, photo uploads, matching system, messaging, and safety features.

## Features

### 🔐 Authentication & User Management
- Custom user registration with email verification
- Secure login/logout system
- Profile creation and editing
- Photo upload with drag-and-drop interface

### 💝 Matching System
- Advanced profile discovery with filters
- Swipe interface (like Tinder)
- Mutual matching system
- Customizable preferences (age, distance, gender)

### 💬 Messaging
- Real-time conversations between matches
- Beautiful chat interface
- Message history and read status

### 🛡️ Safety Features
- User reporting system
- Block functionality
- Profile verification status
- Content moderation tools

### 🎨 Modern UI/UX
- Responsive design with gradient backgrounds
- Smooth animations using GSAP
- Card-based layout
- Mobile-friendly interface

## Tech Stack

- **Backend**: Django 5.2.3
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Styling**: Custom CSS with glassmorphism effects
- **Animations**: GSAP (GreenSock Animation Platform)
- **Icons**: Font Awesome 6.4.0
- **Image Handling**: Pillow

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip

### Local Installation

1. **Clone or copy the project files**
```bash
# The dating_site directory contains all project files
cd dating_site
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install django pillow
```

4. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Populate sample interests**
```bash
python manage.py populate_interests
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Run the development server**
```bash
python manage.py runserver
```

8. **Access the application**
- Website: http://127.0.0.1:8000
- Admin panel: http://127.0.0.1:8000/admin

## Project Structure

```
dating_site/
├── lovematch/              # Main project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/               # User authentication
│   ├── models.py          # Custom user model
│   ├── views.py           # Login/register views
│   ├── forms.py           # Authentication forms
│   └── urls.py
├── profiles/               # User profiles
│   ├── models.py          # Profile, photos, interests
│   ├── views.py           # Profile CRUD operations
│   ├── forms.py           # Profile forms
│   └── management/        # Management commands
├── matching/               # Matching system
│   ├── models.py          # Swipes, matches, preferences
│   ├── views.py           # Swipe logic, match views
│   └── forms.py
├── messaging/              # Chat system
│   ├── models.py          # Conversations, messages
│   ├── views.py           # Chat interface
│   └── urls.py
├── templates/              # HTML templates
│   ├── base.html          # Base template
│   ├── accounts/          # Auth templates
│   ├── profiles/          # Profile templates
│   ├── matching/          # Match templates
│   └── messaging/         # Chat templates
├── static/                 # Static files (optional)
├── media/                  # Uploaded photos
└── manage.py
```

## Key Models

### CustomUser
- Extended Django user with additional fields
- Email-based authentication
- Date of birth for age calculation

### Profile
- User profile information
- Location, bio, preferences
- Education, occupation details
- Smoking/drinking preferences

### Match & Swipe
- Swipe tracking (like/pass)
- Mutual match detection
- Match preferences

### Conversation & Message
- Chat functionality
- Message history
- Read status tracking

## Core Features

### 1. User Registration & Authentication
- Email-based registration
- Profile creation wizard
- Secure password handling

### 2. Profile Management
- Rich profile editing
- Multiple photo uploads
- Interest selection
- Privacy controls

### 3. Discovery System
- Advanced filtering
- Location-based matching
- Age and preference filters
- Random profile ordering

### 4. Matching Algorithm
- Swipe-based interactions
- Mutual like detection
- Instant match notifications
- Match history

### 5. Messaging System
- Real-time chat interface
- Message persistence
- Conversation management
- Match-based messaging

### 6. Safety Features
- User reporting
- Profile blocking
- Content moderation
- Verification system

## Admin Features

Access the Django admin panel to:
- Manage users and profiles
- Review reported content
- Monitor site activity
- Moderate conversations

## Customization

### Adding New Interests
```bash
python manage.py shell
from profiles.models import Interest
Interest.objects.create(name="Your Interest")
```

### Styling Customization
- Edit CSS in template files
- Modify color schemes in base.html
- Update animations in JavaScript sections

### Feature Extensions
- Add more profile fields in models.py
- Implement advanced filtering
- Add notification system
- Integrate with external APIs

## Security Considerations

- CSRF protection enabled
- User input validation
- Image upload restrictions
- Report and block functionality
- Admin content moderation

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## License

This project is for educational purposes. Customize as needed for your use case.

## Support

For issues or questions:
1. Check the Django documentation
2. Review the model definitions
3. Test with sample data
4. Check server logs for errors

---

**LoveMatch** - Where love meets technology! 💕