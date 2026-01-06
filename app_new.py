import streamlit as st
import pandas as pd
import datetime

# --- CONFIG & STYLING ---
st.set_page_config(page_title="MTL Hoops", page_icon="🏀", layout="wide")

# CUSTOM CSS FOR "APP-LIKE" FEEL
st.markdown("""
<style>
    /* 1. GLOBAL FONT & SPACING */
    .stApp { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    .block-container { padding-top: 2rem !important; } /* Reduce top whitespace */
    
    /* 2. CARD DESIGN */
    .hoop-card {
        background-color: #1E1E1E; /* Dark card background */
        border: 1px solid #333;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        transition: transform 0.2s;
    }
    .hoop-card:hover { border-color: #555; }
    
    /* 3. TIME COLUMN (Left) */
    .time-big { font-size: 1.4rem; font-weight: 800; color: #ff4b4b; line-height: 1; }
    .time-small { font-size: 0.85rem; color: #888; margin-top: 4px; }
    
    /* 4. DETAILS COLUMN (Middle) */
    .activity-title { font-size: 1.1rem; font-weight: 600; color: #fff; margin-bottom: 4px; }
    .location-text { font-size: 0.95rem; color: #bbb; display: flex; align-items: center; gap: 6px; }
    
    /* 5. TAGS (Right) */
    .tag-container { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; }
    .price-tag { 
        background-color: #333; 
        color: #eee; 
        padding: 4px 10px; 
        border-radius: 20px; 
        font-size: 0.8rem; 
        font-weight: 600;
        border: 1px solid #444;
    }
    .free-tag {
        background-color: #1b4d2e; /* Dark Green */
        color: #8afcba; /* Light Green text */
        border: 1px solid #2f7a46;
    }
    .source-tag { font-size: 0.75rem; color: #666; text-transform: uppercase; letter-spacing: 1px; }

    /* Hides Streamlit's default elements for cleaner look */
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- HELPER: TIME FORMATTER ---
def format_display_time(time_str):
    try:
        if len(time_str) > 5 and ":" in time_str: 
            time_str = time_str[:5]
        dt = datetime.datetime.strptime(time_str, "%H:%M")
        return dt.strftime("%-I:%M"), dt.strftime("%p") # Returns ("2:15", "PM")
    except:
        return time_str, ""

def format_time_range(start_time, end_time):
    """Format start and end time into a readable range"""
    if pd.isna(end_time) or end_time == "TBD":
        start_main, start_ampm = format_display_time(start_time)
        return f"{start_main} {start_ampm}"
    
    start_main, start_ampm = format_display_time(start_time)
    end_main, end_ampm = format_display_time(end_time)
    
    if start_ampm == end_ampm:
        return f"{start_main} - {end_main} {end_ampm}"
    else:
        return f"{start_main} {start_ampm} - {end_main} {end_ampm}"

# --- LOAD DATA ---
try:
    df = pd.read_csv("master_schedule.csv")
    df['Date'] = df['Date'].astype(str)
    df['Start_Time'] = df['Start_Time'].astype(str)
    df['End_Time'] = df['End_Time'].astype(str)
    
    # --- MAINTENANCE CHECK ---
    # When did we last update? (Simple logic: Check if Jan 2026 data exists)
    # In a real app, you might save a 'meta.json' with the update date.
    today = datetime.date.today()
    if today > datetime.date(2026, 3, 20): # Warning after Winter Season
        st.sidebar.error("⚠️ Data might be stale! Winter season ended.")
        
except FileNotFoundError:
    st.error("🚨 Data missing. Run 'python data_consolidator.py' first.")
    st.stop()

# --- SIDEBAR FILTERS ---
with st.sidebar:
    st.image("https://em-content.zobj.net/source/apple/391/basketball_1f3c0.png", width=50)
    st.title("Filters")
    
    all_boroughs = sorted(df['Borough'].astype(str).unique().tolist())
    selected_boroughs = st.multiselect("📍 Neighborhood", all_boroughs, default=[])
    
    st.divider()
    st.caption("Jump to date:")
    start_date = st.date_input("Start Date", datetime.date(2026, 1, 5), label_visibility="collapsed")

# --- MAIN LAYOUT ---
st.markdown("### 🏀 Montreal Hoops Schedule")

week_days = [start_date + datetime.timedelta(days=i) for i in range(7)]
tabs = st.tabs([d.strftime("%a %d") for d in week_days])

for i, day in enumerate(week_days):
    with tabs[i]:
        day_str = str(day)
        day_name = day.strftime("%A")
        
        mask_date = df['Date'] == day_str
        mask_recurring = df['Date'].str.contains(day_name, case=False, na=False)
        mask_ymca_recurring = (df['Source'] == 'YMCA') & df['Date'].str.contains('Recurring', case=False, na=False)
        
        daily_df = df[mask_date | mask_recurring | mask_ymca_recurring].copy()
        
        # Remove YMCA duplicates
        if not daily_df.empty:
            daily_df = daily_df.drop_duplicates(subset=['Source', 'Location', 'Activity', 'Start_Time'], keep='first')
        
        if selected_boroughs:
            daily_df = daily_df[daily_df['Borough'].isin(selected_boroughs)]
        
        if not daily_df.empty:
            daily_df = daily_df.sort_values("Start_Time")
            
            for _, row in daily_df.iterrows():
                # Format Data
                time_main, time_ampm = format_display_time(row["Start_Time"])
                time_range = format_time_range(row["Start_Time"], row.get("End_Time", "TBD"))
                is_free = "Free" in str(row['Price']) or row['Price'] == "0.0"
                price_class = "price-tag free-tag" if is_free else "price-tag"
                price_text = "FREE" if is_free else row['Price']
                
                # Render HTML Card
                st.markdown(f"""
                <div class="hoop-card">
                    <div style="display: flex; align-items: center;">
                        <div style="flex: 0 0 80px; text-align: center; border-right: 1px solid #333; padding-right: 12px; margin-right: 12px;">
                            <div class="time-big">{time_main}</div>
                            <div class="time-small">{time_ampm}</div>
                        </div>
                        
                        <div style="flex: 1;">
                            <div class="activity-title">{row['Activity']}</div>
                            <div class="location-text">📍 {row['Location']} <span style="color:#555">•</span> {row['Borough']}</div>
                            <div style="font-size: 0.85rem; color: #888; margin-top: 4px;">⏰ {time_range}</div>
                        </div>
                        
                        <div class="tag-container">
                            <span class="{price_class}">{price_text}</span>
                            <span class="source-tag">{row['Source']}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(f"No runs found for {day.strftime('%A')}.")