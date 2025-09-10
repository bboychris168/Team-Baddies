import streamlit as st
import json
from datetime import datetime
import pandas as pd
import hashlib
import uuid

# Set up page config
st.set_page_config(page_title="Team Baddies", page_icon="🏸", layout="wide")

# Initialize session state for admin login
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

# Admin credentials (in production, use environment variables or secure storage)
ADMIN_PASSWORD = "admin123"  # This should be hashed in production

# Helper functions
def save_data():
    with open("player_list.json", "w") as file:
        json.dump(player_list, file, indent=4)
    with open("audit_trail.json", "w") as file:
        json.dump(audit_trail, file, indent=4)
    with open("court_layout.json", "w") as file:
        json.dump(court_layout, file, indent=4)

def verify_password(password):
    # In production, use proper password hashing
    return password == ADMIN_PASSWORD

def add_audit_log(action, details, user_type="user"):
    audit_trail.append({
        "action": action,
        "details": details,
        "user_type": user_type,
        "timestamp": datetime.now().isoformat()
    })

# Load data
try:
    with open("player_list.json", "r") as file:
        player_list = json.load(file)
except FileNotFoundError:
    player_list = {
        "Monday": {"Players": [], "Waitlist": []},
        "Tuesday": {"Players": [], "Waitlist": []},
        "Thursday": {"Players": [], "Waitlist": []}
    }

try:
    with open("court_layout.json", "r") as file:
        court_layout = json.load(file)
except FileNotFoundError:
    court_layout = {
        "courts": [
            {"id": 1, "level": "beginner", "name": "Court 1"},
            {"id": 2, "level": "beginner", "name": "Court 2"},
            {"id": 3, "level": "intermediate", "name": "Court 3"},
            {"id": 4, "level": "intermediate", "name": "Court 4"},
            {"id": 5, "level": "advanced", "name": "Court 5"},
            {"id": 6, "level": "advanced", "name": "Court 6"}
        ]
    }
st.set_page_config(page_title="Team Baddies", page_icon="🏸", layout="wide")

# Initialize session state for admin login
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

# Admin credentials (in production, use environment variables or secure storage)
ADMIN_PASSWORD = "admin123"  # This should be hashed in production

# Apply custom CSS for styling
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
        color: #212529;
    }
    .header {
        text-align: center;
        color: #0d6efd;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
    }
    .subheader {
        text-align: center;
        color: #495057;
        font-size: 1.75rem;
        font-weight: 600;
    }
    .card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
    }
    .court {
        background-color: #90EE90;
        border: 2px solid #2d6a4f;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem;
        text-align: center;
    }
    .court-beginner {
        background-color: #98FB98;
    }
    .court-intermediate {
        background-color: #90EE90;
    }
    .court-advanced {
        background-color: #3CB371;
    }
    .player-card {
        background-color: white;
        border-radius: 8px;
        padding: 0.5rem;
        margin: 0.25rem;
        border: 1px solid #dee2e6;
    }
    .skill-badge {
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .skill-beginner {
        background-color: #cfe2ff;
        color: #084298;
    }
    .skill-intermediate {
        background-color: #fff3cd;
        color: #664d03;
    }
    .skill-advanced {
        background-color: #d1e7dd;
        color: #0f5132;
    }
    .admin-panel {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 2rem;
    }
    /* Custom button styles */
    .stButton>button {
        background-color: #0d6efd;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #0b5ed7;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1 class='title'>🏸 Team Baddies</h1>", unsafe_allow_html=True)
st.markdown("<h2 class='subheader'>Badminton Roster Management</h2>", unsafe_allow_html=True)

# Helper functions
def save_data():
    with open("player_list.json", "w") as file:
        json.dump(player_list, file, indent=4)
    with open("audit_trail.json", "w") as file:
        json.dump(audit_trail, file, indent=4)
    with open("court_layout.json", "w") as file:
        json.dump(court_layout, file, indent=4)

def verify_password(password):
    # In production, use proper password hashing
    return password == ADMIN_PASSWORD

def add_audit_log(action, details, user_type="user"):
    audit_trail.append({
        "action": action,
        "details": details,
        "user_type": user_type,
        "timestamp": datetime.now().isoformat()
    })

# Load existing player list or initialize a new one
try:
    with open("player_list.json", "r") as file:
        player_list = json.load(file)
except FileNotFoundError:
    player_list = {"Monday": {"Players": [], "Waitlist": []},
                   "Tuesday": {"Players": [], "Waitlist": []},
                   "Thursday": {"Players": [], "Waitlist": []}}

# Load audit trail or initialize a new one
try:
    with open("audit_trail.json", "r") as file:
        audit_trail = json.load(file)
except FileNotFoundError:
    audit_trail = []

# Sidebar navigation
st.sidebar.markdown("## Navigation")
page = st.sidebar.radio("Select Page", ["Home", "Court Layout", "Admin Panel"])

# Sidebar day selection (only show on Home page)
if page == "Home":
    day = st.sidebar.radio("Select a day:", ["Monday", "Tuesday", "Thursday"])

# Admin Login in Sidebar
with st.sidebar:
    st.markdown("---")
    st.markdown("## Admin Access")
    if not st.session_state.admin_logged_in:
        admin_password = st.text_input("Admin Password", type="password")
        if st.button("Login"):
            if verify_password(admin_password):
                st.session_state.admin_logged_in = True
                st.success("Successfully logged in as admin!")
            else:
                st.error("Incorrect password!")
    else:
        if st.button("Logout"):
            st.session_state.admin_logged_in = False
            st.experimental_rerun()

# Main content area
st.markdown("<h1 class='header'>🏸 Team Baddies</h1>", unsafe_allow_html=True)

if page == "Home":
    # Create three columns: courts, player list, and input
    col1, col2, col3 = st.columns([2, 2, 1])

# Home Page
if page == "Home":
    # Create three columns: courts, player list, and input
    col1, col2, col3 = st.columns([2, 2, 1])
    
    # First column: Court Layout
    with col1:
        st.markdown("<div class='card'><h3>Court Layout</h3>", unsafe_allow_html=True)
        
        # Display courts in a grid
        for i in range(0, len(court_layout["courts"]), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(court_layout["courts"]):
                    court = court_layout["courts"][i + j]
                    with cols[j]:
                        st.markdown(
                            f"<div class='court court-{court['level']}'>"
                            f"<h4>{court['name']}</h4>"
                            f"<p>{court['level'].title()} Level</p>"
                            "</div>",
                            unsafe_allow_html=True
                        )
        st.markdown("</div>", unsafe_allow_html=True)

# Second column: Player Lists
with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"<h3>Players for {day}</h3>", unsafe_allow_html=True)
    
    players = player_list[day]["Players"]
    waitlist = player_list[day]["Waitlist"]
    
    # Convert players list to DataFrame for better display
    if players:
        df = pd.DataFrame(players)
        df.columns = ["Name", "Skill Level"]
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No players added yet.")
    
    st.markdown(f"<p class='counter'>Player Count: {len(players)}/27</p>", unsafe_allow_html=True)
    
    st.markdown("<h3>Waitlist</h3>", unsafe_allow_html=True)
    if waitlist:
        df_wait = pd.DataFrame(waitlist)
        df_wait.columns = ["Name", "Skill Level"]
        st.dataframe(df_wait, use_container_width=True)
    else:
        st.info("No players in waitlist.")
    
    st.markdown(f"<p class='counter'>Waitlist Count: {len(waitlist)}/20</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Third column: Player Management
with col3:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>Add Player</h3>", unsafe_allow_html=True)
    
    new_player = st.text_input("Name:")
    skill_level = st.selectbox("Skill Level:", ["Beginner", "Intermediate", "Advanced"])
    
    if st.button("Add Player", key="add_player", use_container_width=True):
        if new_player:
            if len(players) < 27:
                players.append([new_player, skill_level])
                st.success(f"{new_player} added to {day} player list!")
            elif len(waitlist) < 20:
                waitlist.append([new_player, skill_level])
                st.success(f"{new_player} added to {day} waitlist!")
            else:
                st.error(f"Sorry, both lists are full for {day}.")
            
            add_audit_log("Added", f"{new_player} ({skill_level}) - {day}")
            save_data()
        else:
            st.error("Please enter a name.")
    
    st.markdown("<h3>Remove Player</h3>", unsafe_allow_html=True)
    
    # Remove from player list
    if players:
        remove_player = st.selectbox(
            "From player list:",
            ["None"] + [p[0] for p in players]
        )
        if remove_player != "None":
            if st.button("Remove from List", key="remove_player"):
                player_data = next(p for p in players if p[0] == remove_player)
                players.remove(player_data)
                st.success(f"Removed {remove_player}")
                add_audit_log("Removed", f"{remove_player} from {day} list")
                save_data()
    
    # Remove from waitlist
    if waitlist:
        remove_waitlist = st.selectbox(
            "From waitlist:",
            ["None"] + [p[0] for p in waitlist]
        )
        if remove_waitlist != "None":
            if st.button("Remove from Waitlist", key="remove_waitlist"):
                player_data = next(p for p in waitlist if p[0] == remove_waitlist)
                waitlist.remove(player_data)
                st.success(f"Removed {remove_waitlist}")
                add_audit_log("Removed", f"{remove_waitlist} from {day} waitlist")
                save_data()
    
    st.markdown("</div>", unsafe_allow_html=True)

# Court Layout Page
elif page == "Court Layout":
    if not st.session_state.admin_logged_in:
        st.warning("Please log in as admin to access the court layout settings.")
    else:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h2>Court Layout Management</h2>", unsafe_allow_html=True)
        
        # Edit courts
        for i, court in enumerate(court_layout["courts"]):
            cols = st.columns([1, 2, 1])
            with cols[0]:
                st.markdown(f"#### Court {i + 1}")
            with cols[1]:
                new_level = st.selectbox(
                    f"Level for Court {i + 1}",
                    ["beginner", "intermediate", "advanced"],
                    index=["beginner", "intermediate", "advanced"].index(court["level"]),
                    key=f"court_{i}"
                )
            with cols[2]:
                new_name = st.text_input("Court Name", court["name"], key=f"name_{i}")
            
            court_layout["courts"][i]["level"] = new_level
            court_layout["courts"][i]["name"] = new_name
        
        if st.button("Save Court Layout"):
            save_data()
            add_audit_log("Updated Court Layout", "Court configuration changed", "admin")
            st.success("Court layout updated successfully!")
        
        st.markdown("</div>", unsafe_allow_html=True)

# Admin Panel Page
elif page == "Admin Panel":
    if not st.session_state.admin_logged_in:
        st.warning("Please log in as admin to access the admin panel.")
    else:
        st.markdown("<div class='admin-panel'>", unsafe_allow_html=True)
        st.markdown("<h2>Admin Panel</h2>", unsafe_allow_html=True)
        
        # Audit Trail
        st.markdown("<h3>Audit Trail</h3>", unsafe_allow_html=True)
        audit_df = pd.DataFrame(audit_trail)
        st.dataframe(audit_df, use_container_width=True)
        
        # Player Statistics
        st.markdown("<h3>Player Statistics</h3>", unsafe_allow_html=True)
        total_players = sum(len(player_list[day]["Players"]) for day in player_list)
        total_waitlist = sum(len(player_list[day]["Waitlist"]) for day in player_list)
        
        cols = st.columns(3)
        cols[0].metric("Total Active Players", total_players)
        cols[1].metric("Total Waitlisted", total_waitlist)
        cols[2].metric("Total Courts", len(court_layout["courts"]))
        
        # Export Data
        st.markdown("<h3>Export Data</h3>", unsafe_allow_html=True)
        if st.button("Download Audit Trail CSV"):
            audit_df.to_csv("audit_trail_export.csv", index=False)
            st.success("Audit trail exported to audit_trail_export.csv")
        
        st.markdown("</div>", unsafe_allow_html=True)
