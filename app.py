import streamlit as st
import pandas as pd
import datetime

# --- CONFIG & STYLING ---
st.set_page_config(page_title="MTL Hoops", page_icon="🏀", layout="wide")

st.markdown("""
<style>
    /* Dark Theme & Glow Effects */
    .stApp { background-color: #0E1117; font-family: 'Inter', sans-serif; }
    
    /* Sidebar Logo */
    .sidebar-logo { 
        font-size: 1.8rem; 
        font-weight: 700; 
        color: #fff; 
        display: flex; 
        align-items: center; 
        gap: 15px; 
        margin-bottom: 20px; 
        font-family: 'Montserrat', 'Arial Black', sans-serif;
        letter-spacing: -1px;
    }
    .sidebar-logo .highlight { color: #FF4B4B; text-shadow: 0 0 10px rgba(255,75,75,0.3); }
    .basketball-icon {
        font-size: 2.8rem;
        filter: drop-shadow(0 0 8px rgba(255,75,75,0.4));
        animation: bounce 2s infinite;
    }
    @keyframes bounce {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-3px); }
    }

    /* Time Header (The Red Glow Bar) */
    .time-header {
        background: linear-gradient(90deg, #1E2130 0%, #13151C 100%);
        padding: 12px 20px;
        border-radius: 8px 8px 0 0;
        border-left: 5px solid #FF4B4B;
        display: flex;
        align-items: center;
        margin-top: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .time-text { font-size: 1.4rem; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 10px; }

    /* Session Row */
    .session-row {
        background-color: #161924;
        border-bottom: 1px solid #262A3B;
        padding: 16px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 1px solid #262A3B;
        border-right: 1px solid #262A3B;
    }
    .session-row:last-child { border-radius: 0 0 8px 8px; }
    
    .gym-name { font-size: 1rem; font-weight: 600; color: #E0E0E0; }
    .gym-loc { font-size: 0.85rem; color: #888; margin-top: 4px; }
    
    /* Price Tag */
    .tag { background-color: #1E293B; color: #94A3B8; padding: 6px 12px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; border: 1px solid #334155; }
    .tag.free { background-color: #064E3B; color: #34D399; border-color: #065F46; }
    
    /* Navigation Buttons */
    div[data-testid="column"] button {
        background-color: #1E293B !important;
        color: #FF4B4B !important;
        border: 1px solid #FF4B4B !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="column"] button:hover {
        background-color: #FF4B4B !important;
        color: white !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3) !important;
    }

    header {visibility: hidden;} 
    .block-container { padding-top: 2rem !important; }
    
    /* Mobile Sidebar Fix */
    @media (max-width: 768px) {
        .sidebar .sidebar-content {
            width: 100% !important;
        }
        /* Make sidebar toggle more visible on mobile */
        .sidebar-toggle {
            background-color: #FF4B4B !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 8px 12px !important;
            margin: 10px !important;
            font-weight: bold !important;
        }
        /* Ensure filters are visible when sidebar is open */
        section[data-testid="stSidebar"] {
            min-width: 280px !important;
            background-color: rgba(14, 17, 23, 0.95) !important;
            backdrop-filter: blur(10px) !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
try:
    df = pd.read_csv("master_schedule.csv")
    df['Date'] = df['Date'].astype(str)
    df['Start_Time'] = df['Start_Time'].astype(str)
except FileNotFoundError:
    st.error("🚨 Missing 'master_schedule.csv'. Please create the file!")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
        <div class="sidebar-logo">
            <span class="basketball-icon">🏀</span>
            <div>
                <span>MTL</span><span class="highlight">HOOPS</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.caption("v1.2 • Winter 2026")
    
    # Neighborhood Filter
    all_boroughs = sorted(df['Borough'].unique().tolist())
    selected_boroughs = st.multiselect("Neighborhood", all_boroughs, default=[])
    
    # Source/Type Filter
    all_sources = sorted(df['Source'].unique().tolist())
    display_sources = []
    for source in all_sources:
        if source == "City":
            display_sources.append("City (Free)")
        else:
            display_sources.append(source)
    
    selected_display_sources = st.multiselect("Type", display_sources, default=[])
    
    # Convert back to original source names for filtering
    selected_sources = []
    for display_source in selected_display_sources:
        if display_source == "City (Free)":
            selected_sources.append("City")
        else:
            selected_sources.append(display_source)
    
    st.divider()
    st.caption("Jump to Date:")
    # Default to a Monday in Jan 2026 to show data immediately
    start_date = st.date_input("Date", datetime.date(2026, 1, 13), label_visibility="collapsed")
    
    st.divider()
    st.markdown("### Alerts")
    st.caption("Get notified about new runs.")
    st.text_input("Email", placeholder="you@email.com")
    st.button("Subscribe")

# --- MAIN CONTENT ---
st.title("Montreal Open Gyms")

# Mobile-friendly filters (shown only on mobile)
if st.checkbox("📱 Show Filters", help="Filter by neighborhood and type"):
    mobile_col1, mobile_col2 = st.columns(2)
    with mobile_col1:
        mobile_boroughs = st.multiselect("📍 Area", all_boroughs, key="mobile_boroughs")
        if mobile_boroughs:
            selected_boroughs = mobile_boroughs
    with mobile_col2:
        mobile_sources = st.multiselect("🏢 Type", display_sources, key="mobile_sources") 
        if mobile_sources:
            selected_display_sources = mobile_sources
            # Convert mobile selections
            selected_sources = []
            for display_source in selected_display_sources:
                if display_source == "City (Free)":
                    selected_sources.append("City")
                else:
                    selected_sources.append(display_source)

# Week Navigation
if 'week_offset' not in st.session_state:
    st.session_state.week_offset = 0

# Navigation controls
nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])

with nav_col1:
    if st.button("← Previous Week", key="prev_week"):
        st.session_state.week_offset -= 7
        st.rerun()

with nav_col3:
    if st.button("Next Week →", key="next_week"):
        st.session_state.week_offset += 7
        st.rerun()

with nav_col2:
    # Calculate current week range
    current_start = start_date + datetime.timedelta(days=st.session_state.week_offset)
    current_end = current_start + datetime.timedelta(days=6)
    st.markdown(f"<div style='text-align: center; font-weight: 600; color: #FF4B4B; padding: 8px;'>{current_start.strftime('%b %d')} - {current_end.strftime('%b %d, %Y')}</div>", unsafe_allow_html=True)

# Tabs for Current Week (7 days)
week_days = [start_date + datetime.timedelta(days=i + st.session_state.week_offset) for i in range(7)]
tabs = st.tabs([d.strftime("%a %d") for d in week_days])

for i, day in enumerate(week_days):
    with tabs[i]:
        day_str = str(day)
        day_name = day.strftime("%A") # e.g., "Monday"
        
        # LOGIC: Matches specific dates OR "Every Monday"
        mask_date = df['Date'] == day_str
        mask_recurring = df['Date'].str.contains(f"Every {day_name}", case=False, na=False)
        
        daily_df = df[mask_date | mask_recurring].copy()
        
        if selected_boroughs:
            daily_df = daily_df[daily_df['Borough'].isin(selected_boroughs)]
            
        if selected_sources:
            daily_df = daily_df[daily_df['Source'].isin(selected_sources)]
            
        if daily_df.empty:
            st.info(f"No runs found for {day_name}.")
        else:
            # Group by Time for Layout
            daily_df = daily_df.sort_values("Start_Time")
            grouped = daily_df.groupby("Start_Time")
            
            st.markdown(f"**{len(daily_df)} runs found**")
            
            for start_time, runs in grouped:
                # Nice Time Format (14:15 -> 2:15 PM)
                try:
                    dt = datetime.datetime.strptime(start_time[:5], "%H:%M")
                    nice_time = dt.strftime("%-I:%M %p")
                except: nice_time = start_time
                
                # Header
                st.markdown(f"""
                <div class="time-header">
                    <div class="time-text">🕒 {nice_time}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Rows
                for _, row in runs.iterrows():
                    price = row['Price']
                    tag_class = "tag free" if ("Free" in str(price) or price=="0.00") else "tag"
                    
                    st.markdown(f"""
                    <div class="session-row">
                        <div>
                            <div class="gym-name">{row['Activity']}</div>
                            <div class="gym-loc">📍 {row['Location']} <span style="color:#444">•</span> {row['Borough']}</div>
                        </div>
                        <div class="{tag_class}">{price}</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)