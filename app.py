import os

from flask import Flask, request, session, render_template, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta, date
from random import choice, random

from helpers import apology, login_required

from models import *
from quotes import StoicQuotes


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


def backfill_habit_data(user_id):
    """Backfill habit data for user with ID 1 starting from 2017"""
    if user_id != 1:
        return
        
    user = User.query.get(1)
    if not user:
        return
        
    # Set registration date to 2017
    new_registration_date = date(2017, 1, 1)
    user.registration_date = new_registration_date
    
    # Get all habits for the user
    habits = Habit.query.filter_by(user_id=1).all()
    
    # Generate all dates from 2017 to now
    start_date = new_registration_date
    end_date = date.today()
    delta = end_date - start_date
    dates = [start_date + timedelta(days=i) for i in range(delta.days + 1)]
    
    # Delete existing logs for these habits
    for habit in habits:
        HabitLog.query.filter(HabitLog.habit_id == habit.id).delete()
    
    # Create new logs with 70% probability of being True
    for habit in habits:
        new_logs = []
        for log_date in dates:
            done = random() < 0.7  # 70% chance of being True
            log = HabitLog(
                date=log_date,
                done=done,
                habit_id=habit.id
            )
            new_logs.append(log)
        db.session.bulk_save_objects(new_logs)
    
    db.session.commit()


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

        # If this is user ID 1, backfill their habit data
        backfill_habit_data(user.id)

        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("register.html")


# Add a new route to trigger backfill manually (optional)
@app.route("/backfill", methods=["POST"])
@login_required
def backfill():
    """Manually trigger backfill for user 1"""
    if session["user_id"] != 1:
        return apology("unauthorized", 403)
    
    backfill_habit_data(1)
    return redirect("/habits")


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

# Initialize quotes
quotes = StoicQuotes()

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

    # Get a random quote
    daily_quote = quotes.get_random_quote()

    return render_template("index.html", 
                         user=user,
                         weeks_data=weeks_data, 
                         weeks_lived=weeks_lived,
                         total_weeks=total_weeks,
                         today=date.today(),
                         quote=quotes.get_random_quote())


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


def setup_and_backfill_user_one():
    """Set up three habits for user 1 and backfill their data from 2017"""
    user = User.query.get(1)
    if not user:
        return
        
    # Set registration date to 2017
    new_registration_date = date(2017, 1, 1)
    user.registration_date = new_registration_date
    
    # Delete existing habits and their logs
    Habit.query.filter_by(user_id=1).delete()
    
    # Create three habits
    habits_to_create = [
        {"name": "Stretching", "color": "#AF7AC5"},
        {"name": "Running", "color": "#48C9B0"},
        {"name": "Reading", "color": "#5DADE2"}
    ]
    
    created_habits = []
    for habit_data in habits_to_create:
        habit = Habit(
            name=habit_data["name"],
            description="",
            background_color=habit_data["color"],
            user_id=1
        )
        db.session.add(habit)
        created_habits.append(habit)
    
    db.session.commit()
    
    # Generate all dates from 2017 to now
    start_date = new_registration_date
    end_date = date.today()
    delta = end_date - start_date
    dates = [start_date + timedelta(days=i) for i in range(delta.days + 1)]
    
    # Create logs for each habit
    for habit in created_habits:
        new_logs = []
        for log_date in dates:
            done = random.random() < 0.7  # 70% chance of being True
            log = HabitLog(
                date=log_date,
                done=done,
                habit_id=habit.id
            )
            new_logs.append(log)
        db.session.bulk_save_objects(new_logs)
    
    db.session.commit()


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

        # After creating a new habit, if it's user 1 and they have no habits yet
        if session["user_id"] == 1 and len(Habit.query.filter_by(user_id=1).all()) == 0:
            setup_and_backfill_user_one()

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
            current_year=current_year,
            today=date.today()
        )


@app.route("/update_habit_name", methods=["POST"])
@login_required
def update_habit_name():
    habit_id = request.form.get("habit_id")
    new_name = request.form.get("name")

    if not habit_id or not new_name:
        return apology("Invalid habit or name", 400)

    habit = Habit.query.filter_by(id=habit_id, user_id=session["user_id"]).first()
    if not habit:
        return apology("Invalid habit", 403)

    habit.name = new_name
    db.session.commit()

    return redirect("/habits")

    
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


def calculate_habit_stats(habit):
    """Calculate statistics for a given habit"""
    today = date.today()
    logs = HabitLog.query.filter_by(habit_id=habit.id).order_by(HabitLog.date).all()
    
    if not logs:
        return {
            'total_days': 0,
            'completed_days': 0,
            'completion_rate': 0,
            'current_streak': 0,
            'longest_streak': 0,
            'last_30_days': 0
        }
    
    # Basic counts
    completed_logs = [log for log in logs if log.done]
    total_days = len(logs)
    completed_days = len(completed_logs)
    completion_rate = (completed_days / total_days * 100) if total_days > 0 else 0
    
    # Calculate streaks
    current_streak = 0
    longest_streak = 0
    temp_streak = 0
    
    # Sort logs by date for streak calculation
    sorted_logs = sorted(logs, key=lambda x: x.date, reverse=True)
    
    # Calculate current streak
    for log in sorted_logs:
        if log.done:
            current_streak += 1
        else:
            break
            
    # Calculate longest streak
    for log in sorted(logs, key=lambda x: x.date):
        if log.done:
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 0
            
    # Calculate last 30 days completion rate
    thirty_days_ago = today - timedelta(days=30)
    recent_logs = [log for log in logs if log.date >= thirty_days_ago]
    completed_recent = len([log for log in recent_logs if log.done])
    last_30_days_rate = (completed_recent / len(recent_logs) * 100) if recent_logs else 0
    
    return {
        'total_days': total_days,
        'completed_days': completed_days,
        'completion_rate': round(completion_rate, 1),
        'current_streak': current_streak,
        'longest_streak': longest_streak,
        'last_30_days': round(last_30_days_rate, 1)
    }

@app.route("/stats")
@login_required
def stats():
    """Show habit statistics"""
    user = User.query.get(session["user_id"])
    if user is None:
        return redirect("/login")
        
    habits = Habit.query.filter_by(user_id=user.id).all()
    
    # Calculate statistics for each habit
    habits_stats = {}
    for habit in habits:
        habits_stats[habit.id] = calculate_habit_stats(habit)
    
    return render_template("stats.html", 
                         habits=habits,
                         habits_stats=habits_stats)