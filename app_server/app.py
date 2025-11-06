# app.py - App Server (Flask + SQLAlchemy + JWT)
import os
import re
import datetime
from functools import wraps

from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.exc import IntegrityError

from models import db, User

# ---------- Configuration ----------
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecretkey')  # override in production
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# initialize db with app
db.init_app(app)

# ---------- Helpers ----------
EMAIL_RE = re.compile(r"^[^@]+@[^@]+\.[^@]+$")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth = request.headers.get('Authorization', None)
        if auth and auth.startswith('Bearer '):
            token = auth.split(' ', 1)[1]

        if not token:
            return jsonify({'message':'Token is missing!'}), 401

        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload.get('id')
            current_user = User.query.get(user_id)
            if not current_user:
                return jsonify({'message':'User not found'}), 401
        except ExpiredSignatureError:
            return jsonify({'message':'Token has expired'}), 401
        except InvalidTokenError as e:
            return jsonify({'message':'Invalid token', 'error': str(e)}), 401
        except Exception as e:
            return jsonify({'message':'Token error', 'error': str(e)}), 401

        return f(current_user, *args, **kwargs)
    return decorated

# ---------- Routes ----------
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'message':'Invalid request (no JSON)'}), 400

    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    course = (data.get('course') or '').strip()
    password = data.get('password') or ''

    if not (name and email and password):
        return jsonify({'message':'Name, email and password are required'}), 400

    if not EMAIL_RE.match(email):
        return jsonify({'message':'Invalid email format'}), 400

    try:
        hashed = generate_password_hash(password)
        user = User(name=name, email=email, course=course, password_hash=hashed)
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message':'User already exists'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message':'Database error', 'error': str(e)}), 500

    return jsonify({'message':'registered successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'message':'Invalid request (no JSON)'}), 400

    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not (email and password):
        return jsonify({'message':'Email and password required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'message':'Invalid credentials'}), 401

    payload = {
        'id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    if isinstance(token, bytes):
        token = token.decode('utf-8')

    return jsonify({'token': token, 'user': user.to_dict()}), 200

@app.route('/api/change_password', methods=['POST'])
@token_required
def change_password(current_user):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'message':'Invalid request (no JSON)'}), 400

    old = data.get('old_password') or ''
    new = data.get('new_password') or ''
    if not (old and new):
        return jsonify({'message':'Both old and new password required'}), 400

    if not check_password_hash(current_user.password_hash, old):
        return jsonify({'message':'Old password incorrect'}), 401

    current_user.password_hash = generate_password_hash(new)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message':'Database error', 'error': str(e)}), 500

    return jsonify({'message':'Password changed successfully'}), 200

@app.route('/api/get_user', methods=['GET'])
@token_required
def get_user(current_user):
    return jsonify(current_user.to_dict()), 200

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status':'ok'}), 200

# ---------- Startup ----------
if __name__ == '__main__':
    # create tables if missing (safe for dev). For production, use migrations.
    with app.app_context():
        db.create_all()

    web_host = os.environ.get('APP_HOST', '0.0.0.0')
    web_port = int(os.environ.get('APP_PORT', 5001))
    app.run(host=web_host, port=web_port, debug=True)
