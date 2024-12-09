import os

from flask import Flask, request, session, render_template, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta, date
from random import choice

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
                    birthdate=birthdate,
                    registration_date=datetime.today().date())

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


def get_color_for_percentage(percentage):
    """
    Returns a color between red and green based on the percentage.
    percentage should be between 0 and 1
    """
    # Ensure percentage is between 0 and 1
    percentage = max(0, min(1, percentage))
    
    # Convert percentage to a color between red (255,0,0) and green (0,255,0)
    red = int(255 * (1 - percentage))
    green = int(255 * percentage)
    
    return f"rgb({red}, {green}, 0)"

def calculate_week_habits_percentage(habits, start_date, end_date):
    """
    Calculate the percentage of completed habits for a given week.
    Returns a float between 0 and 1.
    """
    total_possible = len(habits) * 7  # Total possible habit entries for the week
    if total_possible == 0:
        return 0
        
    completed = 0
    
    for habit in habits:
        # Get habit logs for this week
        week_logs = HabitLog.query.filter(
            HabitLog.habit_id == habit.id,
            HabitLog.date >= start_date,
            HabitLog.date <= end_date,
            HabitLog.done == True
        ).count()
        
        completed += week_logs
    
    return completed / total_possible

def get_week_data(birthdate, registration_date, habits):
    """
    Generate data for each week including whether it was lived and its color based on habit completion.
    Returns a list of dictionaries containing week information.
    """
    today = datetime.today().date()
    total_weeks = 80 * 52
    weeks_data = []
    
    # Calculate the Monday of the birth week
    birth_week_monday = birthdate - timedelta(days=birthdate.weekday())
    
    # Calculate the Monday of the registration week
    registration_week_monday = registration_date - timedelta(days=registration_date.weekday())
    
    for week_num in range(total_weeks):
        week_start = birth_week_monday + timedelta(weeks=week_num)
        week_end = week_start + timedelta(days=6)
        
        week_data = {
            'lived': week_end < today,
            'start_date': week_start,
            'end_date': week_end,
            'is_post_registration': week_start >= registration_week_monday
        }
        
        if week_data['lived'] and week_data['is_post_registration']:
            # Calculate habit completion percentage for post-registration weeks
            percentage = calculate_week_habits_percentage(habits, week_start, week_end)
            week_data['color'] = get_color_for_percentage(percentage)
        else:
            week_data['color'] = 'black' if week_data['lived'] else '#dcdcdc'
            
        weeks_data.append(week_data)
    
    return weeks_data

@app.route("/")
@login_required
def index():
    user = User.query.get(session["user_id"])
    if user is None:
        return redirect("/login")

    # Get all habits for the user
    habits = Habit.query.filter_by(user_id=user.id).all()
    
    # Get weeks data including habit completion colors
    weeks_data = get_week_data(user.birthdate, user.registration_date, habits)
    
    # Calculate basic statistics
    total_weeks = 80 * 52
    weeks_lived = sum(1 for week in weeks_data if week['lived'])

    return render_template("index.html", 
                         user=user,
                         weeks_data=weeks_data, 
                         weeks_lived=weeks_lived,
                         total_weeks=total_weeks)


def calculate_weeks_lived(birthdate):
    today = datetime.today().date()
    weeks_lived = (today - birthdate).days // 7
    return weeks_lived


def generate_week_columns(start_of_year, end_of_year):
    """
    Generate a 2D list of dates for the habit grid.
    Each row represents a week, with 7 columns (Monday to Sunday).
    """
    week_columns = []
    current_date = start_of_year

    while current_date <= end_of_year:
        week = []
        for _ in range(7):  # Create 7 days (Mon-Sun)
            if current_date <= end_of_year:
                week.append(current_date)
                current_date += timedelta(days=1)
            else:
                week.append(None)  # Fill remaining cells with None
        week_columns.append(week)
    return week_columns


def generate_background_color():
    """
    Returns a random hex color string from a curated list of aesthetically pleasing colors.
    """
    colors = [
        "#5DADE2",  # Blue
        "#58D68D",  # Green
        "#F39C12",  # Orange
        "#AF7AC5",  # Purple
        "#F1948A",  # Pink
        "#48C9B0",  # Teal
        "#F7DC6F",  # Yellow
    ]
    return choice(colors)


@app.route("/habits", methods=["GET", "POST"])
@login_required
def habits():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")

        if not name:
            return apology("must provide habit name", 400)

        habit = Habit(name=name, 
                      description=description,
                      background_color=generate_background_color(),
                      user_id=session["user_id"])
        db.session.add(habit)
        db.session.commit()
        return redirect("/habits")

    else:
        current_year = int(request.args.get("year", datetime.today().year))
        
        # Calculate dates for the year
        start_date = date(current_year, 1, 1)
        end_date = date(current_year, 12, 31)
        
        # Generate week columns for the entire year
        week_columns = []
        
        # Get the weekday of January 1st (0 = Monday, 6 = Sunday)
        first_weekday = start_date.weekday()
        
        # Add empty days before January 1st in the first week
        first_week = [None] * first_weekday
        
        # Fill the rest of the first week
        temp_date = start_date
        while len(first_week) < 7:
            if temp_date <= end_date:
                first_week.append(temp_date)
                temp_date += timedelta(days=1)
            else:
                first_week.append(None)
        
        week_columns.append(first_week)
        
        # Start from the first day of the second week
        current_date = start_date + timedelta(days=(7 - first_weekday))
        
        # Generate remaining weeks
        while current_date <= end_date:
            week = []
            for _ in range(7):  # 7 days per week
                if current_date <= end_date:
                    week.append(current_date)
                    current_date += timedelta(days=1)
                else:
                    week.append(None)  # Add None for days beyond the year
            week_columns.append(week)

        user = User.query.get(session["user_id"])
        habits = Habit.query.filter_by(user_id=user.id).all()
        
        # Get all habit logs for the year
        for habit in habits:
            logs = HabitLog.query.filter(
                HabitLog.habit_id == habit.id,
                HabitLog.date >= start_date,
                HabitLog.date <= end_date
            ).all()
            
            # Convert logs to a dictionary for easier lookup
            habit.log_dict = {log.date: log.done for log in logs}

        return render_template(
            "habits.html",
            habits=habits,
            week_columns=week_columns,
            current_year=current_year
        )

    
@app.route("/delete_habit", methods=["POST"])
@login_required
def delete_habit():
    habit_id = request.form.get("habit_id")

    # Fetch the habit to delete
    habit = Habit.query.filter_by(id=habit_id, user_id=session["user_id"]).first()
    if not habit:
        return apology("Habit not found", 404)

    # Delete the habit and its associated logs
    HabitLog.query.filter_by(habit_id=habit.id).delete()
    db.session.delete(habit)
    db.session.commit()

    return redirect("/habits")


@app.route("/toggle_habit_log", methods=["POST"])
@login_required
def toggle_habit_log():
    # Get the habit_id and date from the form
    habit_id = request.form.get("habit_id")
    date_str = request.form.get("date")
    if not habit_id or not date_str:
        return apology("Invalid habit or date", 400)

    date = datetime.strptime(date_str, "%Y-%m-%d").date()

    # Ensure the habit_id is valid
    habit = Habit.query.get(habit_id)
    if not habit or habit.user_id != session["user_id"]:
        return apology("Invalid habit", 403)

    # Toggle the habit log for the given date
    habit_log = HabitLog.query.filter_by(habit_id=habit_id, date=date).first()
    if habit_log:
        habit_log.done = not habit_log.done
    else:
        habit_log = HabitLog(habit_id=habit_id, date=date, done=True)
        db.session.add(habit_log)

    db.session.commit()
    return redirect(f"/habits?year={date.year}")
