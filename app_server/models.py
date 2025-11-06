# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    course = db.Column(db.String(100), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {'id': self.id, 'email': self.email, 'name': self.name, 'course': self.course}
