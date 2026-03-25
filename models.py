from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    buildings = db.relationship('Building', backref='owner', lazy=True)
    paths = db.relationship('EvacuationPath', backref='creator', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Building(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    floors = db.Column(db.Integer, default=1)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    hazards = db.relationship('Hazard', backref='building', lazy=True)
    paths = db.relationship('EvacuationPath', backref='building', lazy=True)

class Hazard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    building_id = db.Column(db.Integer, db.ForeignKey('building.id'), nullable=False)
    floor = db.Column(db.Integer, default=1)
    x = db.Column(db.Integer, nullable=False)
    y = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    intensity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class EvacuationPath(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    building_id = db.Column(db.Integer, db.ForeignKey('building.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    start_x = db.Column(db.Integer, nullable=False)
    start_y = db.Column(db.Integer, nullable=False)
    end_x = db.Column(db.Integer, nullable=False)
    end_y = db.Column(db.Integer, nullable=False)
    path_data = db.Column(db.Text, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    steps = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_path(self):
        return json.loads(self.path_data)