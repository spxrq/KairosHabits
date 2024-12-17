# KairosHabits

A habit tracking application with a Memento Mori calendar integration, developed by Sean Park.

## Overview

KairosHabits combines the philosophical concept of Memento Mori (remember that you will die) with practical habit tracking. The application visualizes your life in weeks while incorporating habit tracking data to show not just the passage of time, but how well you've lived each week through your habits.

## Features

### Memento Mori Calendar
- Visualizes your entire life in weeks (80 years)
- Weeks before registration are marked in black (time passed)
- Weeks after registration are color-coded based on habit completion:
  - Green indicates high habit completion rate
  - Red indicates low habit completion rate
  - Black indicates weeks passed before registration

![Memento Mori Calendar](docs/calendar.png)

### Habit Tracking
- Create and manage multiple habits
- Edit habits names
- Daily tracking with simple toggle interface
- Visual feedback through color-coding
- Switch to different years

![Habits](docs/habits.png)

### Habit Statistics
- Comprehensive statistics dashboard for each habit:
  - Overall completion rate
  - Current streak tracking
  - Longest streak achieved
  - Last 30 days performance
  - Total days tracked and completed
- Visual presentation of statistics in easy-to-read cards
- Color-coded habit categories for better organization

![Statistics Dashboard](docs/statistics.png)

### Stoic Inspiration
- Curated collection of Stoic quotes
- Random daily quote display for motivation
- Philosophical foundation aligning with the Memento Mori concept

## Purpose

KairosHabits goes beyond traditional habit tracking by connecting daily actions with life's finite nature. By showing your completed habits in the context of your entire life span, it creates a powerful visual reminder that:
1. Time is limited and precious
2. Every week is an opportunity for improvement
3. Small daily actions accumulate into visible progress

The color gradient from red to green in the weekly boxes serves as an immediate feedback mechanism, showing not just that time has passed, but how well you've used it through your habits.

## Installation

### Prerequisites
- Python 3.10 or higher
- PostgreSQL database

### Setup
1. Clone the repository:
```bash
git clone https://github.com/spxrq/KairosHabits.git
cd KairosHabits
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
export DATABASE_URL=postgresql://[username]:[password]@localhost/kairoshabits
```

5. Initialize the database:
```bash
flask db upgrade
```

6. Run the application:
```bash
flask run
```

## Dependencies
- Flask
- Flask-Session
- Flask-SQLAlchemy
- psycopg2-binary

## Project Structure
```
KairosHabits/
├── app.py              # Main application file
├── docs/              # Documentation and screenshots
│   ├── calendar.png
│   ├── habits.png
│   ├── statistics.png
├── helpers.py          # Helper functions
├── models.py           # Database models
├── quotes.py           # Stoic quotes collection
├── requirements.txt    # Project dependencies
├── static/            # Static files (CSS, JS)
└── templates/         # HTML templates
```

## Future Enhancements
- Export habit data analytics
- Custom habit categories
- Weekly reflection prompts
- Progress sharing capabilities

## Acknowledgments
The project draws inspiration from:
- Stoic philosophy
- [The Memento Mori concept](https://en.wikipedia.org/wiki/Memento_mori)
- Various habit tracking applications

---