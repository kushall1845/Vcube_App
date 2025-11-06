
# Simple helper to create database (for sqlite default)
from app import app
from models import db
with app.app_context():
    db.create_all()
    print('Database created.')
