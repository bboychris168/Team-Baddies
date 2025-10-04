import streamlit as st
import json
from datetime import datetime
import pandas as pd

# Configuration
st.set_page_config(page_title="Team Baddies", page_icon="🏸", layout="wide")
ADMIN_PASSWORD = "admin123"

# Initialize session state
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

# Data Management Functions
def load_data():
    """Load all application data"""
    try:
        with open("player_list.json", "r") as f:
            players = json.load(f)
    except FileNotFoundError:
        players = {
            "Monday": {"Players": [], "Waitlist": []},
            "Tuesday": {"Players": [], "Waitlist": []},
            "Thursday": {"Players": [], "Waitlist": []}
        }
    
    try:
        with open("court_layout.json", "r") as f:
            courts = json.load(f)
    except FileNotFoundError:
        courts = {
            "courts": [
                {"id": 1, "level": "beginner", "name": "Court 1", "position": {"row": 0, "col": 0}, "active": True},
                {"id": 2, "level": "beginner", "name": "Court 2", "position": {"row": 0, "col": 1}, "active": True},
                {"id": 3, "level": "intermediate", "name": "Court 3", "position": {"row": 1, "col": 0}, "active": True},
                {"id": 4, "level": "intermediate", "name": "Court 4", "position": {"row": 1, "col": 1}, "active": True},
                {"id": 5, "level": "advanced", "name": "Court 5", "position": {"row": 2, "col": 0}, "active": True},
                {"id": 6, "level": "advanced", "name": "Court 6", "position": {"row": 2, "col": 1}, "active": True}
            ],
            "layout_settings": {
                "rows": 3, "cols": 4, "center_name": "Team Baddies Badminton Center",
                "total_courts": 6
            }
        }
    
    try:
        with open("audit_trail.json", "r") as f:
            audit = json.load(f)
    except FileNotFoundError:
        audit = []
    
    return players, courts, audit

def save_data(players, courts, audit):
    """Save all application data"""
    with open("player_list.json", "w") as f:
        json.dump(players, f, indent=2)
    with open("court_layout.json", "w") as f:
        json.dump(courts, f, indent=2)
    with open("audit_trail.json", "w") as f:
        json.dump(audit, f, indent=2)

def add_audit_log(audit, action, details, user_type="user"):
    """Add entry to audit trail"""
    audit.append({
        "action": action, "details": details, "user_type": user_type,
        "timestamp": datetime.now().isoformat()
    })

# Court Image Generation
# NOTE: Court layout and image export functionality removed per request.

# UI Components
def render_css():
    """Render custom CSS"""
    st.markdown("""
    <style>
    .main { background-color: #f8f9fa; color: #212529; }
    .header { text-align: center; color: #0d6efd; font-size: 2.5rem; font-weight: 700; margin-bottom: 1.5rem; }
    .card { background-color: white; border-radius: 10px; padding: 1.5rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); margin-bottom: 1.5rem; }
    .skill-beginner { background-color: #28a745; color: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.875rem; font-weight: 600; }
    .skill-intermediate { background-color: #fd7e14; color: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.875rem; font-weight: 600; }
    .skill-advanced { background-color: #dc3545; color: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.875rem; font-weight: 600; }
    .stButton>button { background-color: #0d6efd; color: white; border: none; border-radius: 6px; padding: 0.5rem 1rem; font-weight: 600; }
    .stButton>button:hover { background-color: #0b5ed7; transform: translateY(-2px); }
    </style>
    """, unsafe_allow_html=True)

def sidebar_navigation():
    """Render sidebar navigation and admin login"""
    st.sidebar.markdown("## Navigation")
    page = st.sidebar.radio("Select Page", ["Home", "Admin Panel"])
    
    day = "Monday"
    if page == "Home":
        day = st.sidebar.radio("Select a day:", ["Monday", "Tuesday", "Thursday"])
    
    # Admin login
    st.sidebar.markdown("---\n## Admin Access")
    if not st.session_state.admin_logged_in:
        password = st.sidebar.text_input("Admin Password", type="password")
        if st.sidebar.button("Login"):
            if password == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.sidebar.success("Logged in as admin!")
                st.rerun()
            else:
                st.sidebar.error("Incorrect password!")
    else:
        if st.sidebar.button("Logout"):
            st.session_state.admin_logged_in = False
            st.rerun()
    
    return page, day

def render_player_management(players, day, audit, courts):
    """Render player management section"""
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("<div class='card'><h3>Players for {}</h3>".format(day), unsafe_allow_html=True)
        
        player_list = players[day]["Players"]
        waitlist = players[day]["Waitlist"]
        
        if player_list:
            st.markdown("**Active Players:**")
            for i, (name, skill) in enumerate(player_list, 1):
                st.markdown(f"""
                <div style='display: flex; justify-content: space-between; align-items: center; 
                           padding: 0.5rem; margin: 0.25rem 0; background: #f8f9fa; border-radius: 5px;'>
                    <span><strong>{i}.</strong> {name}</span>
                    <span class='skill-{skill.lower()}'>{skill}</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No players added yet.")
        
        st.markdown(f"<p style='color: #28a745; font-weight: bold;'>Player Count: {len(player_list)}/27</p>", unsafe_allow_html=True)
        
        st.markdown("<h3>Waitlist</h3>", unsafe_allow_html=True)
        if waitlist:
            for i, (name, skill) in enumerate(waitlist, 1):
                st.markdown(f"""
                <div style='display: flex; justify-content: space-between; align-items: center; 
                           padding: 0.5rem; margin: 0.25rem 0; background: #fff3cd; border-radius: 5px;'>
                    <span><strong>{i}.</strong> {name}</span>
                    <span class='skill-{skill.lower()}'>{skill}</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No players in waitlist.")
        
        st.markdown(f"<p style='color: #fd7e14; font-weight: bold;'>Waitlist Count: {len(waitlist)}/20</p></div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='card'><h3>Add Player</h3>", unsafe_allow_html=True)
        
        new_player = st.text_input("Name:", key=f"new_player_{day}")
        skill_level = st.selectbox("Skill Level:", ["Beginner", "Intermediate", "Advanced"], key=f"skill_{day}")
        
        if st.button("Add Player", use_container_width=True, key=f"add_{day}"):
            if new_player:
                if len(player_list) < 27:
                    player_list.append([new_player, skill_level])
                    st.success(f"{new_player} added to {day} player list!")
                elif len(waitlist) < 20:
                    waitlist.append([new_player, skill_level])
                    st.success(f"{new_player} added to {day} waitlist!")
                else:
                    st.error(f"Sorry, both lists are full for {day}.")
                add_audit_log(audit, "Added", f"{new_player} ({skill_level}) - {day}")
                # Persist immediately
                save_data(players, courts, audit)
                st.rerun()
            else:
                st.error("Please enter a name.")
        
        st.markdown("<h3>Remove Player</h3>", unsafe_allow_html=True)
        
        # Remove from player list
        if player_list:
            remove_player = st.selectbox("From player list:", ["None"] + [p[0] for p in player_list], key=f"remove_player_{day}")
            if remove_player != "None" and st.button("Remove from List", key=f"remove_list_{day}"):
                player_data = next(p for p in player_list if p[0] == remove_player)
                player_list.remove(player_data)
                add_audit_log(audit, "Removed", f"{remove_player} from {day} list")
                # Persist immediately
                save_data(players, courts, audit)
                st.success(f"Removed {remove_player}")
                st.rerun()
        
        # Remove from waitlist
        if waitlist:
            remove_waitlist = st.selectbox("From waitlist:", ["None"] + [p[0] for p in waitlist], key=f"remove_wait_{day}")
            if remove_waitlist != "None" and st.button("Remove from Waitlist", key=f"remove_wait_btn_{day}"):
                player_data = next(p for p in waitlist if p[0] == remove_waitlist)
                waitlist.remove(player_data)
                add_audit_log(audit, "Removed", f"{remove_waitlist} from {day} waitlist")
                save_data(players, courts, audit)
                st.success(f"Removed {remove_waitlist}")
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

def render_court_layout_page(courts, audit):
    # NOTE: Court layout functionality removed — use the Admin Panel for player/court data management via JSON files.
    st.warning("Court Layout functionality has been removed from this app. You can still manage players and data in the Admin Panel.")

def render_admin_panel(players, courts, audit):
    """Render admin panel"""
    if not st.session_state.admin_logged_in:
        st.warning("Please log in as admin to access the admin panel.")
        return
    
    st.markdown("<h2>Admin Panel</h2>", unsafe_allow_html=True)
    
    # Statistics
    total_players = sum(len(players[day]["Players"]) for day in players)
    total_waitlist = sum(len(players[day]["Waitlist"]) for day in players)
    total_courts = len([c for c in courts["courts"] if c.get("active", True)])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Active Players", total_players)
    col2.metric("Total Waitlisted", total_waitlist)
    col3.metric("Total Courts", total_courts)
    
    # Audit trail
    st.markdown("### Audit Trail")
    if audit:
        audit_df = pd.DataFrame(audit)
        st.dataframe(audit_df, use_container_width=True)
        
        # Export option
        if st.button("📥 Download Audit Trail CSV"):
            csv = audit_df.to_csv(index=False)
            st.download_button("Download CSV", data=csv, file_name=f"audit_trail_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")
    else:
        st.info("No audit trail entries yet.")

# Main Application
def main():
    """Main application entry point"""
    # Load data
    players, courts, audit = load_data()
    
    # Render UI
    render_css()
    st.markdown("<h1 class='header'>🏸 Team Baddies</h1>", unsafe_allow_html=True)
    
    # Navigation
    page, day = sidebar_navigation()
    
    # Page routing
    if page == "Home":
        st.markdown("### 🏸 Badminton Center Summary")
        try:
            court_list = courts.get("courts", [])
            active_courts = [c for c in court_list if c.get("active", True)]
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("🏸 Total Courts", len(active_courts))
            col2.metric("🟢 Beginner", len([c for c in active_courts if c.get("level") == "beginner"]))
            col3.metric("🟠 Intermediate", len([c for c in active_courts if c.get("level") == "intermediate"]))
            col4.metric("🔴 Advanced", len([c for c in active_courts if c.get("level") == "advanced"]))
        except Exception as e:
            st.error(f"Error loading court data: {str(e)}")
        
        st.markdown("---")
        
        # Player management
        st.markdown("### 👥 Player Registration")
        render_player_management(players, day, audit, courts)
    
    # The 'Court Layout' page has been removed from the UI.
    
    elif page == "Admin Panel":
        render_admin_panel(players, courts, audit)
    
    # Save data
    save_data(players, courts, audit)

if __name__ == "__main__":
    main()
