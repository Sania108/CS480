# config.py

class Config:
    # Replace these with your PostgreSQL credentials
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:Wrongturn@localhost:5432/taxi_rental_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your-secret-key'  # Used for form security (Flask-WTF)