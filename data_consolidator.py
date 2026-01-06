import pandas as pd
import pdfplumber
import requests
from ics import Calendar
import datetime
import pytz
from dateutil import rrule
import warnings
import os 
import re # NEW: For finding time patterns

warnings.filterwarnings("ignore")

# --- CONFIG ---
CITY_JSON_FILE = "city_data.json"
MCGILL_ICS_URL = "https://calendar.google.com/calendar/ical/athleticsmcgill%40gmail.com/public/basic.ics"
OUTPUT_CSV = "master_schedule.csv"

# --- 1. CONCORDIA GENERATOR ---
def get_concordia_data():
    print("Generating Concordia Schedule...")
    data = []
    start_date = datetime.date(2026, 1, 5)
    end_date = datetime.date(2026, 4, 20)
    
    # Downtown (Mon-Fri)
    weekdays = list(rrule.rrule(rrule.DAILY, dtstart=start_date, until=end_date, 
                                byweekday=(rrule.MO, rrule.TU, rrule.WE, rrule.TH, rrule.FR)))
    for d in weekdays:
        data.append({"Source": "Concordia", "Location": "Concordia (Downtown)", "Borough": "Downtown",
                     "Activity": "Open Gym (Basketball)", "Date": d.strftime("%Y-%m-%d"), 
                     "Start_Time": "14:15", "End_Time": "17:15", "Price": "Mem/Drop-in"})

    # Downtown (Sun)
    sundays = list(rrule.rrule(rrule.DAILY, dtstart=start_date, until=end_date, byweekday=(rrule.SU)))
    for d in sundays:
        data.append({"Source": "Concordia", "Location": "Concordia (Downtown)", "Borough": "Downtown",
                     "Activity": "Open Gym (Basketball)", "Date": d.strftime("%Y-%m-%d"), 
                     "Start_Time": "12:00", "End_Time": "15:00", "Price": "Mem/Drop-in"})
    return data

# --- 2. YMCA (FROM CSV DATA) ---
def get_ymca_pdf_data():
    print("Loading YMCA schedules from CSV...")
    data = []
    try:
        df = pd.read_csv("ymca_open_gym_schedule_updated.csv")
        for _, row in df.iterrows():
            # Map location names
            location_map = {
                "Du Parc": "YMCA Du Parc YMCA",
                "Cartierville": "YMCA Cartierville YMCA", 
                "Westmount": "YMCA Westmount YMCA",
                "Notre-Dame-de-Grace": "YMCA Notre-Dame-de-Grâce YMCA"
            }
            
            location = location_map.get(row['Location'], f"YMCA {row['Location']}")
            
            data.append({
                "Source": "YMCA",
                "Location": location,
                "Borough": row['Location'],
                "Activity": "Open Gym (Basketball)",
                "Date": f"Every {row['Day']} (Recurring)",
                "Start_Time": row['Start Time'],
                "End_Time": row['End Time'],
                "Price": "Mem/Drop-in"
            })
    except FileNotFoundError:
        print("⚠️ YMCA CSV not found, using fallback data...")
        # Keep original hard-coded data as fallback
        return get_ymca_fallback_data()
    
    return data

def get_ymca_fallback_data():
    ymca_schedules = {
        "Westmount YMCA": {
            "borough": "Westmount",
            "sessions": [
                {"days": ["Monday"], "time": "06:00", "end_time": "09:00"},
                {"days": ["Wednesday"], "time": "06:00", "end_time": "09:00"},
                {"days": ["Thursday"], "time": "06:00", "end_time": "09:00"},
                {"days": ["Wednesday"], "time": "11:30", "end_time": "14:30"},
                {"days": ["Wednesday"], "time": "14:30", "end_time": "17:30"},
                {"days": ["Thursday"], "time": "14:00", "end_time": "17:00"},
                {"days": ["Sunday"], "time": "16:00", "end_time": "19:00"},
                {"days": ["Monday"], "time": "18:30", "end_time": "21:30"},
                {"days": ["Monday"], "time": "19:45", "end_time": "21:45"},
            ]
        }
    }
    
    data = []
    for location, info in ymca_schedules.items():
        for session in info["sessions"]:
            for day in session["days"]:
                data.append({
                    "Source": "YMCA",
                    "Location": f"YMCA {location}",
                    "Borough": info["borough"],
                    "Activity": "Open Gym (Basketball)",
                    "Date": f"Every {day} (Recurring)",
                    "Start_Time": session["time"],
                    "End_Time": session["end_time"],
                    "Price": "Mem/Drop-in"
                })
    return data

# --- 3. MCGILL (FIXED) ---
def get_mcgill_data():
    print("Fetching McGill ICS...")
    data = []
    try:
        c = Calendar(requests.get(MCGILL_ICS_URL).text)
        local_tz = pytz.timezone('America/Montreal')
        
        for event in c.events:
            if not event.name: continue 
            name = event.name.lower()
            # Only include Pick-Up Basketball events, exclude IM Basketball and badminton
            if "pick-up basketball" not in name: continue
            if "badminton" in name: continue
            
            start_dt = event.begin.astimezone(local_tz)
            if start_dt.date() < datetime.date.today(): continue
            
            end_dt = event.end.astimezone(local_tz)
            data.append({"Source": "McGill", "Location": "McGill Athletics", "Borough": "Downtown",
                         "Activity": "Open Gym (Basketball)", "Date": start_dt.strftime("%Y-%m-%d"), 
                         "Start_Time": start_dt.strftime("%H:%M"), "End_Time": end_dt.strftime("%H:%M"), "Price": "Mem/Drop-in"})
    except Exception as e:
        print(f"⚠️ McGill Error: {e}")
    return data

# --- 4. CITY DATA ---
def get_city_data():
    print("Processing City JSON...")
    data = []
    try:
        df = pd.read_json(CITY_JSON_FILE)
        mask = df['nom_activite'].astype(str).str.contains('basketball|ballon panier|basket', case=False, na=False)
        exclude = df['nom_activite'].astype(str).str.contains('badminton|soccer', case=False, na=False)
        df = df[mask & ~exclude]
        for _, row in df.iterrows():
            clean_date = str(row.get('date_activite'))[:10]
            
            # Extract end time based on location
            location = row['nom_installation']
            end_time = "TBD"
            if "Marguerite" in location:
                end_time = "21:15"
            elif "Monseigneur-Richard" in location:
                end_time = "22:30"
            elif "Notre-Dame-de-Lourdes" in location:
                end_time = "22:00"
            
            data.append({"Source": "City", "Location": location, 
                         "Borough": row.get('nom_arrondissement', 'Montreal'),
                         "Activity": "Open Gym (Basketball)", "Date": clean_date, 
                         "Start_Time": row.get('heure_debut'), "End_Time": end_time, "Price": "Free"})
    except: print("⚠️ City JSON not found.")
    return data

# --- EXECUTE ---
all_rows = []
all_rows.extend(get_concordia_data())
all_rows.extend(get_ymca_pdf_data())
all_rows.extend(get_mcgill_data())
all_rows.extend(get_city_data())

df = pd.DataFrame(all_rows)
df.to_csv(OUTPUT_CSV, index=False)
print(f"\n✅ DONE! Generated '{OUTPUT_CSV}' with {len(df)} games from all sources.")