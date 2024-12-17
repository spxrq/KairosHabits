# Code Review door Sophie Kaandorp en Tarik Ulgen

## 1. Veiligheid en Authenticatie
**Probleem:** Basic authenticatie implementatie zonder sterke wachtwoordvereisten en foutafhandeling.

**Oplossing:**
- Implementeer password_validation library voor wachtwoordcontroles
- Voeg rate limiting toe voor inlogpogingen

**Afweging:** Betere beveiliging vs. gebruikersgemak. Strengere wachtwoordeisen kunnen tot frustratie leiden maar zijn essentieel voor veiligheid.

**Voorbeeld:**
```python
from password_validation import validate_password
from werkzeug.security import generate_password_hash

def register_user(username, password):
    if not validate_password(password, min_length=8, special_chars=True):
        return False
    hash = generate_password_hash(password)
    # Store hash in database
```

## 2. Comments
**Probleem:** De code bevat te weinig inline comments, vooral bij complexe functies zoals `get_week_data()` en `calculate_habit_stats()`. Dit maakt het moeilijk voor andere ontwikkelaars om de logica te begrijpen.

**Oplossing:**
- Voeg strategische comments toe bij complexe berekeningen
- Documenteer belangrijke beslissingen en edge cases
- Gebruik docstrings voor functiedocumentatie

**Afweging:** Te veel comments kunnen de code onoverzichtelijk maken en verouderd raken, te weinig maakt de code moeilijk te begrijpen. Focus op het documenteren van "waarom" in plaats van "wat".

**Voorbeeld:**
Huidige code zonder voldoende comments:
```python
def calculate_weeks_lived(birthdate):
    today = datetime.today().date()
    weeks_lived = (today - birthdate).days // 7
    return weeks_lived
```

Verbeterde versie met nuttige comments:
```python
def calculate_weeks_lived(birthdate):
    today = datetime.today().date()
    # Integer division by 7 ensures we only count complete weeks
    # We use days//7 instead of timedelta(weeks=) for more precise calculation
    weeks_lived = (today - birthdate).days // 7
    return weeks_lived
```

## 3. Error Handling
**Probleem:** Inconsistente foutafhandeling tussen routes.

**Oplossing:**
- Creëer centrale error handler
- Standaardiseer error responses
- Implementeer custom exceptions

**Afweging:** Consistentie vs. flexibiliteit in error responses.

**Voorbeeld:**
```python
class ApiError(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code

@app.errorhandler(ApiError)
def handle_api_error(error):
    return jsonify(error=error.message), error.status_code
```

## 4. Tests en Documentatie
**Probleem:** Gebrek aan tests en documentatie voor complexe functies.

**Oplossing:**
- Voeg pytest test suite toe
- Documenteer functies met docstrings
- Maak setup instructies

**Afweging:** Ontwikkeltijd vs. lange termijn onderhoudbaarheid.

**Voorbeeld:**
```python
def get_week_data(user_id: int, start_date: datetime) -> dict:
    """Calculate weekly habit completion statistics.
    
    Args:
        user_id: The ID of the user
        start_date: Starting date for calculation
        
    Returns:
        Dict containing weekly statistics
    """
```
