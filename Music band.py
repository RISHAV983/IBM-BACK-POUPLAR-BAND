#Database Setup (SQL)
#First, let's define our database schema directly in SQL:
sql
-- band/models.sql
CREATE TABLE IF NOT EXISTS auth_user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME,
    is_superuser BOOLEAN NOT NULL,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(30) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff BOOLEAN NOT NULL,
    is_active BOOLEAN NOT NULL,
    date_joined DATETIME NOT NULL
);


# For SQL statements in Python, you should either:
# 1. Use triple quotes for multi-line SQL, or
# 2. Remove the # comment markers and put the SQL in proper Python string variables

# Corrected version:
band_song_table = """
CREATE TABLE IF NOT EXISTS band_song (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(100) NOT NULL,
    duration INTEGER NOT NULL,
    release_date DATE NOT NULL,
    lyrics TEXT NOT NULL
);
"""

band_photo_table = """
CREATE TABLE IF NOT EXISTS band_photo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(100) NOT NULL,
    image_path VARCHAR(255) NOT NULL,
    event_date DATE NOT NULL,
    description TEXT NOT NULL
);
"""





#CREATE TABLE IF NOT EXISTS 
band_concert (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(255) NOT NULL,
    date DATETIME NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    available_tickets INTEGER NOT NULL
);

#CREATE TABLE IF NOT EXISTS 
band_userconcert (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    concert_id INTEGER NOT NULL,
    attending BOOLEAN NOT NULL DEFAULT 1,
    payment_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    payment_id VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES auth_user (id),
    FOREIGN KEY (concert_id) REFERENCES band_concert (id)
);
Python Implementation
settings.py
python
# band_website/settings.py
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = 'your-secret-key-here'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'band',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'band_website.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'band/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'band_website.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'band/static')]

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# Google Pay settings
GOOGLE_PAY_MERCHANT_ID = 'your_merchant_id'
GOOGLE_PAY_MERCHANT_NAME = 'Band Name'
GOOGLE_PAY_ENVIRONMENT = 'TEST'  # or 'PRODUCTION'
models.py
python
# band/models.py
from django.db import models
from django.contrib.auth.models import User

class Song(models.Model):
    title = models.CharField(max_length=100)
    duration = models.IntegerField(help_text="Duration in seconds")
    release_date = models.DateField()
    lyrics = models.TextField()

    def __str__(self):
        return self.title

class Photo(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='photos/')
    event_date = models.DateField()
    description = models.TextField()

    def __str__(self):
        return self.title

class Concert(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    date = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_tickets = models.IntegerField()

    def __str__(self):
        return f"{self.name} at {self.location}"

class UserConcert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    concert = models.ForeignKey(Concert, on_delete=models.CASCADE)
    attending = models.BooleanField(default=True)
    payment_status = models.CharField(max_length=20, default='pending')
    payment_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ('user', 'concert')

    def __str__(self):
        return f"{self.user.username} - {self.concert.name}"
views.py
python
# band/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import connection
from .models import Song, Photo, Concert, UserConcert
import json
import uuid
from datetime import datetime

def home(request):
    return render(request, 'band/home.html')

def songs(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT title, duration, release_date FROM band_song")
        songs = cursor.fetchall()
    
    song_list = []
    for song in songs:
        minutes, seconds = divmod(song[1], 60)
        song_list.append({
            'title': song[0],
            'duration': f"{minutes}:{seconds:02d}",
            'release_date': song[2]
        })
    
    return render(request, 'band/songs.html', {'songs': song_list})

def photos(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT title, image_path, event_date, description FROM band_photo")
        photos = cursor.fetchall()
    
    photo_list = [{
        'title': photo[0],
        'image_path': photo[1],
        'event_date': photo[2],
        'description': photo[3]
    } for photo in photos]
    
    return render(request, 'band/photos.html', {'photos': photo_list})

def concerts(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT c.id, c.name, c.location, c.date, c.price, c.available_tickets,
                   CASE WHEN uc.user_id IS NOT NULL THEN 1 ELSE 0 END as is_attending
            FROM band_concert c
            LEFT JOIN band_userconcert uc ON c.id = uc.concert_id AND uc.user_id = %s
        """, [request.user.id if request.user.is_authenticated else None])
        concerts = cursor.fetchall()
    
    concert_list = []
    for concert in concerts:
        concert_list.append({
            'id': concert[0],
            'name': concert[1],
            'location': concert[2],
            'date': concert[3],
            'price': concert[4],
            'available_tickets': concert[5],
            'is_attending': bool(concert[6])
        })
    
    return render(request, 'band/concerts.html', {'concerts': concert_list})

@login_required
def toggle_attendance(request, concert_id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id FROM band_userconcert 
                WHERE user_id = %s AND concert_id = %s
            """, [request.user.id, concert_id])
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute("""
                    DELETE FROM band_userconcert 
                    WHERE id = %s
                """, [existing[0]])
                attending = False
            else:
                cursor.execute("""
                    INSERT INTO band_userconcert 
                    (user_id, concert_id, attending, payment_status)
                    VALUES (%s, %s, %s, %s)
                """, [request.user.id, concert_id, True, 'pending'])
                attending = True
            
            return JsonResponse({'success': True, 'attending': attending})
    
    return JsonResponse({'success': False}, status=400)

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, password FROM auth_user 
                WHERE username = %s
            """, [username])
            user_data = cursor.fetchone()
            
            if user_data:
                user_id, db_password = user_data
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('home')
        
        return render(request, 'band/login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'band/login.html')

def user_logout(request):
    logout(request)
    return redirect('home')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO auth_user 
                (username, password, email, is_superuser, is_staff, is_active, date_joined, first_name, last_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                username,
                make_password(password),
                email,
                False,
                False,
                True,
                datetime.now(),
                '',
                ''
            ])
            
            return redirect('login')
    
    return render(request, 'band/register.html')

@login_required
def payment(request, concert_id):
    concert = get_object_or_404(Concert, pk=concert_id)
    
    if request.method == 'POST':
        # Process Google Pay payment
        payment_token = request.POST.get('payment_token')
        payment_id = str(uuid.uuid4())
        
        # In a real app, you would verify the payment with Google Pay API here
        # For demo purposes, we'll just simulate a successful payment
        
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE band_userconcert
                SET payment_status = 'completed', payment_id = %s
                WHERE user_id = %s AND concert_id = %s
            """, [payment_id, request.user.id, concert_id])
            
            cursor.execute("""
                UPDATE band_concert
                SET available_tickets = available_tickets - 1
                WHERE id = %s
            """, [concert_id])
        
        return render(request, 'band/payment_success.html', {'concert': concert})
    
    # Generate Google Pay payment request
    payment_request = {
        "apiVersion": 2,
        "apiVersionMinor": 0,
        "allowedPaymentMethods": [
            {
                "type": "CARD",
                "parameters": {
                    "allowedAuthMethods": ["PAN_ONLY", "CRYPTOGRAM_3DS"],
                    "allowedCardNetworks": ["VISA", "MASTERCARD"]
                },
                "tokenizationSpecification": {
                    "type": "PAYMENT_GATEWAY",
                    "parameters": {
                        "gateway": "example",
                        "gatewayMerchantId": settings.GOOGLE_PAY_MERCHANT_ID
                    }
                }
            }
        ],
        "merchantInfo": {
            "merchantId": settings.GOOGLE_PAY_MERCHANT_ID,
            "merchantName": settings.GOOGLE_PAY_MERCHANT_NAME
        },
        "transactionInfo": {
            "totalPriceStatus": "FINAL",
            "totalPrice": str(concert.price),
            "currencyCode": "USD",
            "countryCode": "US"
        }
    }
    
    return render(request, 'band/payment.html', {
        'concert': concert,
        'payment_request': json.dumps(payment_request),
        'google_pay_environment': settings.GOOGLE_PAY_ENVIRONMENT
    })
urls.py (app)
python
# band/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('songs/', views.songs, name='songs'),
    path('photos/', views.photos, name='photos'),
    path('concerts/', views.concerts, name='concerts'),
    path('concert/<int:concert_id>/toggle/', views.toggle_attendance, name='toggle_attendance'),
    path('concert/<int:concert_id>/payment/', views.payment, name='payment'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
]
urls.py (project)
python
# band_website/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('band.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
HTML Templates
base.html
html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Band Website{% endblock %}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            line-height: 1.6;
        }
        header {
            background: #333;
            color: #fff;
            padding: 1rem 0;
            text-align: center;
        }
        nav {
            background: #444;
            padding: 0.5rem;
        }
        nav a {
            color: #fff;
            text-decoration: none;
            padding: 0.5rem 1rem;
        }
        nav a:hover {
            background: #555;
        }
        .container {
            width: 80%;
            margin: auto;
            padding: 2rem 0;
        }
        .auth-links {
            float: right;
        }
        .messages {
            padding: 1rem;
            margin: 1rem 0;
            background: #f4f4f4;
        }
        .error {
            color: red;
        }
        .success {
            color: green;
        }
    </style>
</head>
<body>
    <header>
        <h1>Our Awesome Band</h1>
    </header>
    <nav>
        <a href="{% url 'home' %}">Home</a>
        <a href="{% url 'songs' %}">Songs</a>
        <a href="{% url 'photos' %}">Photos</a>
        <a href="{% url 'concerts' %}">Concerts</a>
        <div class="auth-links">
            {% if user.is_authenticated %}
                <span>Hello, {{ user.username }}!</span>
                <a href="{% url 'logout' %}">Logout</a>
            {% else %}
                <a href="{% url 'login' %}">Login</a>
                <a href="{% url 'register' %}">Register</a>
            {% endif %}
        </div>
    </nav>
    <div class="container">
        {% if messages %}
        <div class="messages">
            {% for message in messages %}
                <div class="{{ message.tags }}">{{ message }}</div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% block content %}
        {% endblock %}
    </div>
</body>
</html>
home.html
html
Run
{% extends 'band/base.html' %}

{% block title %}Home - Our Awesome Band{% endblock %}

{% block content %}
    <h2>Welcome to Our Band Website!</h2>
    <p>We are an awesome band that plays great music. Check out our songs, photos, and upcoming concerts!</p>
    
    <h3>Latest News</h3>
    <p>Our new album is coming out soon! Stay tuned for updates.</p>
{% endblock %}
songs.html
html
Run
{% extends 'band/base.html' %}

{% block title %}Songs - Our Awesome Band{% endblock %}

{% block content %}
    <h2>Our Songs</h2>
    
    <table>
        <thead>
            <tr>
                <th>Title</th>
                <th>Duration</th>
                <th>Release Date</th>
            </tr>
        </thead>
        <tbody>
            {% for song in songs %}
            <tr>
                <td>{{ song.title }}</td>
                <td>{{ song.duration }}</td>
                <td>{{ song.release_date }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
{% endblock %}
photos.html
html
Run
{% extends 'band/base.html' %}

{% block title %}Photos - Our Awesome Band{% endblock %}

{% block content %}
    <h2>Photo Gallery</h2>
    
    <div class="photo-grid">
        {% for photo in photos %}
        <div class="photo-item">
            <img src="{{ photo.image_path }}" alt="{{ photo.title }}" width="300">
            <h3>{{ photo.title }}</h3>
            <p>{{ photo.event_date }}</p>
            <p>{{ photo.description }}</p>
        </div>
        {% endfor %}
    </div>
{% endblock %}
concerts.html
html
Run
{% extends 'band/base.html' %}

{% block title %}Concerts - Our Awesome Band{% endblock %}

{% block content %}
    <h2>Upcoming Concerts</h2>
    
    <div class="concert-list">
        {% for concert in concerts %}
        <div class="concert-item">
            <h3>{{ concert.name }}</h3>
            <p>Location: {{ concert.location }}</p>
            <p>Date: {{ concert.date }}</p>
            <p>Price: ${{ concert.price }}</p>
            <p>Tickets available: {{ concert.available_tickets }}</p>
            
            {% if user.is_authenticated %}
                <button class="toggle-attendance" 
                        data-concert-id="{{ concert.id }}"
                        data-attending="{{ concert.is_attending|yesno:'true,false' }}">
                    {% if concert.is_attending %}
                        Cancel Attendance
                    {% else %}
                        Attend Concert
                    {% endif %}
                </button>
                
                {% if concert.is_attending and concert.payment_status == 'pending' %}
                    <a href="{% url 'payment' concert.id %}" class="payment-button">Complete Payment</a>
                {% endif %}
            {% else %}
                <p><a href="{% url 'login' %}">Login</a> to attend this concert</p>
            {% endif %}
        </div>
        {% endfor %}
    </div>
    
    <script>
        document.querySelectorAll('.toggle-attendance').forEach(button => {
            button.addEventListener('click', async function() {
                const concertId = this.dataset.concertId;
                const isAttending = this.dataset.attending === 'true';
                
                try {
                    const response = await fetch(`/concert/${concertId}/toggle/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': '{{ csrf_token }}',
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({})
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        if (data.attending) {
                            this.textContent = 'Cancel Attendance';
                            this.dataset.attending = 'true';
                            // Add payment button if needed
                            if (!this.nextElementSibling || !this.nextElementSibling.classList.contains('payment-button')) {
                                const paymentButton = document.createElement('a');
                                paymentButton.href = `/concert/${concertId}/payment/`;
                                paymentButton.className = 'payment-button';
                                paymentButton.textContent = 'Complete Payment';
                                this.insertAdjacentElement('afterend', paymentButton);
                            }
                        } else {
                            this.textContent = 'Attend Concert';
                            this.dataset.attending = 'false';
                            // Remove payment button if exists
                            if (this.nextElementSibling && this.nextElementSibling.classList.contains('payment-button')) {
                                this.nextElementSibling.remove();
                            }
                        }
                        // Reload the page to update all concert items
                        location.reload();
                    }
                } catch (error) {
                    console.error('Error:', error);
                }
            });
        });
    </script>
{% endblock %}
login.html
html
Run
{% extends 'band/base.html' %}

{% block title %}Login - Our Awesome Band{% endblock %}

{% block content %}
    <h2>Login</h2>
    
    {% if error %}
        <p class="error">{{ error }}</p>
    {% endif %}
    
    <form method="post">
        {% csrf_token %}
        <div>
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required>
        </div>
        <div>
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required>
        </div>
        <button type="submit">Login</button>
    </form>
    
    <p>Don't have an account? <a href="{% url 'register' %}">Register here</a></p>
{% endblock %}
register.html
html
Run
{% extends 'band/base.html' %}

{% block title %}Register - Our Awesome Band{% endblock %}

{% block content %}
    <h2>Register</h2>
    
    <form method="post">
        {% csrf_token %}
        <div>
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required>
        </div>
        <div>
            <label for="email">Email:</label>
            <input type="email" id="email" name="email" required>
        </div>
        <div>
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required>
        </div>
        <button type="submit">Register</button>
    </form>
    
    <p>Already have an account? <a href="{% url 'login' %}">Login here</a></p>
{% endblock %}
payment.html
html
Run
{% extends 'band/base.html' %}

{% block title %}Payment - Our Awesome Band{% endblock %}

{% block content %}
    <h2>Complete Payment for {{ concert.name }}</h2>
    <p>Amount: ${{ concert.price }}</p>
    
    <div id="google-pay-button"></div>
    
    <script src="https://pay.google.com/gp/p/js/pay.js"></script>
    <script>
        const paymentRequest = {{ payment_request|safe }};
        const paymentsClient = new google.payments.api.PaymentsClient({
            environment: '{{ google_pay_environment|lower }}'
        });
        
        function onGooglePayLoaded() {
            paymentsClient.isReadyToPay({
                apiVersion: 2,
                apiVersionMinor: 0,
                allowedPaymentMethods: paymentRequest.allowedPaymentMethods
            }).then(function(response) {
                if (response.result) {
                    addGooglePayButton();
                }
            }).catch(function(err) {
                console.error('Error checking Google Pay readiness:', err);
            });
        }
        
        function addGooglePayButton() {
            const button = paymentsClient.createButton({
                onClick: onGooglePaymentButtonClicked,
                buttonColor: 'black',
                buttonType: 'pay'
            });
            document.getElementById('google-pay-button').appendChild(button);
        }
        
        function onGooglePaymentButtonClicked() {
            paymentsClient.loadPaymentData(paymentRequest).then(function(paymentData) {
                processPayment(paymentData);
            }).catch(function(err) {
                console.error('Error loading payment data:', err);
            });
        }
        
        function processPayment(paymentData) {
            const paymentToken = paymentData.paymentMethodData.tokenizationData.token;
            
            fetch(window.location.href, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': '{{ csrf_token }}'
                },
                body: `payment_token=${encodeURIComponent(paymentToken)}`
            }).then(response => {
                if (response.ok) {
                    window.location.href = "{% url 'concerts' %}";
                } else {
                    alert('Payment processing failed');
                }
            }).catch(error => {
                console.error('Error:', error);
                alert('Payment processing failed');
            });
        }
        
        window.onGooglePayLoaded = onGooglePayLoaded;
    </script>
    <script async src="https://pay.google.com/gp/p/js/pay.js" onload="onGooglePayLoaded()"></script>
{% endblock %}
payment_success.html
html
Run
{% extends 'band/base.html' %}

{% block title %}Payment Successful - Our Awesome Band{% endblock %}

{% block content %}
    <h2>Payment Successful!</h2>
    <p>Thank you for purchasing tickets to {{ concert.name }}.</p>
    <p>Your payment has been processed successfully.</p>
    <p><a href="{% url 'concerts' %}">Back to concerts</a></p>
{% endblock %}
Admin Setup
python
# band/admin.py
from django.contrib import admin
from .models import Song, Photo, Concert, UserConcert

admin.site.register(Song)
admin.site.register(Photo)
admin.site.register(Concert)
admin.site.register(UserConcert)

