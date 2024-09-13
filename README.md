# Django Social Networking API

### Assignment link
https://drive.google.com/file/d/1zjNqjpcvJG843RnJk9Y_CqPLb5tVBuL1/view

## 1. Prerequisites
Before setting up the project, ensure you have the following installed:

* Python 3.10 or later
* PostgreSQL 14 or later

## 2. Setup with Python Virtual Environment
```
git clone git@github.com:arbaazdev/socialnetwork.git
cd socialnetwork
```

## b. Create and Activate Virtual Environment
```
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

## c. Install Dependencies
```
pip install -r requirements.txt
```

## d. Configure the Database

### 1. Create PostgreSQL Database:
Log in to PostgreSQL and create a new database and user:
```
sudo -u postgres psql 
```
Create database
```
postgres=# CREATE DATABASE socialnetwork;
```

### 2. Update Django Settings:
Ensure the DATABASES setting in socailnetwork/settings.py matches your PostgreSQL setup: (If you are changing username and password)
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'socialnetwork',
        'USER': 'user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## e. Run Migrations
```
python manage.py migrate
```

## f. Create a Superuser (optional)
```
python manage.py createsuperuser
```

## g. Run the Development Server
```
python manage.py runserver
```

## h. Import API collection 
I am using thunderclient extension in vscode for API testing. But Postman client will also work. Find and import "Social Network APIs.json" file.

## i. API authentication
Signup and Login both APIs generate token
```
"token": "c8d94068cf440902e72ce45bbc8768b70721a981"
```

Use this token wherever authentication is required
```
Authorization "Token c8d94068cf440902e72ce45bbc8768b70721a981"
```

Everything is included in API collection but token needs to be change as per user.
