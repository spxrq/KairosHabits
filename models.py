from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    registration_date = db.Column(db.Date, nullable=False)
    habits = db.relationship('Habit', backref='user', lazy=True)

class Habit(db.Model):
    __tablename__ = "habits"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    logs = db.relationship('HabitLog', backref='habit', lazy=True)

class HabitLog(db.Model):
    __tablename__ = "habit_logs"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    done = db.Column(db.Boolean, nullable=False)
    habit_id = db.Column(db.Integer, db.ForeignKey('habits.id'), nullable=False)