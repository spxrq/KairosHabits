# Beoordeling KairosHabits

## Belangrijke Features

### 1. Memento Mori Kalender met Habit Integratie
Een unieke feature die uw levensweken visualiseert en koppelt aan habit prestaties:
- Bekijk `get_week_data()` in app.py voor de complexe logica die zowel leeftijd, registratiedatum en habit completion combineert
- De kleurcodering van weken (rood naar groen) geeft direct visueel feedback over habit prestaties
- Effectieve visualisatie van "tijd die voorbij is" (zwart) vs "tijd sinds registratie" (gekleurd)

### 2. Demo Data Generatie
In `backfill_habit_data()` en `setup_and_backfill_user_one()` heb ik een slim systeem gemaakt om de app te demonstreren:
- Automatisch genereren van drie voorbeeldhabits (Stretching, Running, Reading) voor de eerste gebruiker
- Historische data vanaf 2017 wordt gegenereerd met 70% succeskans voor elk habit
- Maakt het mogelijk om de lange-termijn functionaliteit van de app direct te demonstreren
- Gebruikt bulk database operaties voor efficiënte data-insertie

### 3. Habit Statistieken Visualisatie
De statistieken pagina toont:
- Huidige streak tracking
- Longest streak berekening
- Laatste 30 dagen prestaties
- Totaal aantal dagen getracked
- Overall completion rate

## Belangrijke Beslissingen

### 1. Van Maandelijks naar Wekelijks Overzicht
**Oorspronkelijk idee:** Het leven weergeven in maanden met habit tracking op dagelijkse basis.

**Waarom niet handig:**
- Maanden hebben verschillende lengtes (28-31 dagen)
- Te veel detail voor levenslang overzicht (960 maanden vs 4160 weken)
- Maandelijkse statistieken waren te grof voor habit vorming

**Nieuwe oplossing:**
Wekelijks overzicht met dagelijkse habit tracking. Dit werkt beter omdat:
- Weken zijn consistente eenheden (altijd 7 dagen)
- Geeft beter gevoel van urgentie (je ziet weken voorbij gaan)
- Sluit aan bij natuurlijke planningsritme van mensen

Het project heeft bewezen dat dit de juiste keuze was, vooral omdat gebruikers een beter gevoel krijgen voor hun voortgang op zowel korte als lange termijn.

### 2. Van Opgeslagen naar Berekende Statistieken
**Oorspronkelijk idee:** Statistieken (streaks, completion rates) opslaan in aparte database tabel.

**Waarom niet handig:**
- Risico op inconsistentie tussen opgeslagen en werkelijke data
- Extra complexiteit bij het updaten van habits
- Meer database ruimte nodig

**Nieuwe oplossing:**
Statistieken real-time berekenen met efficiënte queries. Dit is beter omdat:
- Garandeert altijd actuele en correcte data
- Simpeler codebase zonder extra tabellen
- Geen synchronisatie nodig tussen habit logs en statistieken

Nu het project is afgerond, blijkt dit nog steeds de juiste keuze - de performance is goed en de code is betrouwbaarder.

### 3. Van Lege naar Voorgevulde Demo Account
**Oorspronkelijk idee:** Alle gebruikers beginnen met een lege habit tracker.

**Waarom niet handig:**
- Moeilijk om functionaliteit te demonstreren
- Gebruikers zien niet direct het potentieel van de app
- Geen voorbeeld van hoe de app er na langdurig gebruik uitziet

**Nieuwe oplossing:**
Automatische backfill voor eerste gebruiker met:
- Drie voorbeeldhabits (Stretching, Running, Reading)
- Realistische data vanaf 2017 (70% completion rate)
- Automatische generatie bij account aanmaak

Deze oplossing blijkt ideaal voor demonstratie doeleinden en heeft het testen significant verbeterd.

## Technische Hoogstandjes

1. Efficiënte demo data generatie:
```python
def backfill_habit_data(user_id):
    if user_id != 1:
        return
        
    # Generate logs with 70% completion rate
    for habit in habits:
        new_logs = []
        for log_date in dates:
            done = random() < 0.7  # 70% chance of being True
            log = HabitLog(date=log_date, done=done, habit_id=habit.id)
            new_logs.append(log)
        db.session.bulk_save_objects(new_logs)
```
Deze functie maakt het mogelijk om jaren aan realistische data te genereren voor demonstratie doeleinden.

2. Dynamische kleurberekening voor weken:
```python
def get_color_for_percentage(percentage):
    percentage = max(0, min(1, percentage))
    red = int(255 * (1 - percentage))
    green = int(255 * percentage)
    return f"rgb({red}, {green}, 0)"
```
Een elegante oplossing voor het visualiseren van voortgang.

3. Slimme week data berekening:
```python
if week_data['lived'] and week_data['is_post_registration']:
    percentage = calculate_week_habits_percentage(habits, week_start, week_end)
    week_data['color'] = get_color_for_percentage(percentage)
else:
    week_data['color'] = 'black' if week_data['lived'] else '#dcdcdc'
```
Deze code combineert levenstijd, registratiedatum en habit prestaties in één visueel systeem.
