import os

from flask import Flask, request, session, render_template, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta

from helpers import apology, login_required

from models import *

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
db.init_app(app)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Ensure email was submitted
        if not email:
            return apology("must provide email", 403)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 403)

        # Query database for username
        user = User.query.filter_by(email=email).first()

        # Ensure username exists and password is correct
        if user is None or not check_password_hash(user.password_hash, password):
            return apology("invalid email and/or password", 403)
        
        # Remember which user has logged in
        session["user_id"] = user.id

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        first_name = request.form.get("first_name")
        email = request.form.get("email")
        birthdate = request.form.get("birthdate")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure email was submitted
        if not email:
            return apology("must provide email", 400)
        
        # Ensure password was submitted
        if not password or not confirmation:
            return apology("must provide password", 400)
        
        # Ensure that the passwords match
        if password != confirmation:
            return apology("passwords don't match", 400)

        # Query database for email
        user = User.query.filter_by(email=email).first()

        # Ensure that user doesn't already exist
        if user:
            return apology("email already exists", 400)
        
        # Insert email and password into database
        user = User(email=email, 
                    first_name=first_name,
                    password_hash=generate_password_hash(password), 
                    birthdate=birthdate)

        # Commit changes to users database
        db.session.add(user)
        db.session.commit()

        # Remember which user has logged in
        session["user_id"] = user.id

        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/")


@app.route("/")
@login_required
def index():
    if not session.get("user_id"):
        return redirect("/login")

    user = User.query.get(session["user_id"])
    weeks_lived = calculate_weeks_lived(user.birthdate)
    total_weeks = 80 * 52

    return render_template("index.html", user=user, weeks_lived=weeks_lived, total_weeks=total_weeks)


def calculate_weeks_lived(birthdate):
    today = datetime.today().date()
    weeks_lived = (today - birthdate).days // 7
    return weeks_lived


@app.route("/habits", methods=["GET", "POST"], endpoint='habits')
@login_required
def habits():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")

        if not name:
            return apology("must provide habit name", 400)

        habit = Habit(name=name, description=description, user_id=session["user_id"])
        db.session.add(habit)
        db.session.commit()
        return redirect("/habits")
    else:
        user = User.query.get(session["user_id"])
        habits = Habit.query.filter_by(user_id=user.id).all()
        start_of_year = datetime(datetime.today().year, 1, 1).date()
        weeks_in_year = (datetime(datetime.today().year + 1, 1, 1).date() - start_of_year).days // 7
        return render_template("habits.html", habits=habits, start_of_year=start_of_year, weeks_in_year=weeks_in_year, timedelta=timedelta)


@app.route("/toggle_habit_log", methods=["POST"], endpoint='toggle_habit_log')
@login_required
def toggle_habit_log():
    habit_id = request.form.get("habit_id")
    date_str = request.form.get("date")
    date = datetime.strptime(date_str, "%Y-%m-%d").date()

    habit_log = HabitLog.query.filter_by(habit_id=habit_id, date=date).first()
    if habit_log:
        habit_log.done = not habit_log.done
    else:
        habit_log = HabitLog(habit_id=habit_id, date=date, done=True)
        db.session.add(habit_log)

    db.session.commit()
    return redirect("/habits")