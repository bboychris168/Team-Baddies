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
            {"id": 1, "level": "beginner", "name": "Court 1", "position": {"row": 0, "col": 0}, "active": True},
            {"id": 2, "level": "beginner", "name": "Court 2", "position": {"row": 0, "col": 1}, "active": True},
            {"id": 3, "level": "intermediate", "name": "Court 3", "position": {"row": 1, "col": 0}, "active": True},
            {"id": 4, "level": "intermediate", "name": "Court 4", "position": {"row": 1, "col": 1}, "active": True},
            {"id": 5, "level": "advanced", "name": "Court 5", "position": {"row": 2, "col": 0}, "active": True},
            {"id": 6, "level": "advanced", "name": "Court 6", "position": {"row": 2, "col": 1}, "active": True}
        ],
        "layout_settings": {
            "rows": 3,
            "cols": 4,
            "center_name": "Team Baddies Badminton Center"
        }
    }

try:
    with open("audit_trail.json", "r") as file:
        audit_trail = json.load(file)
except FileNotFoundError:
    audit_trail = []
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
        cursor: move;
        transition: all 0.3s ease;
        position: relative;
        min-height: 80px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .court:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    .court-beginner {
        background: linear-gradient(135deg, #28a745, #20c997);
        border-color: #198754;
        color: white;
    }
    .court-intermediate {
        background: linear-gradient(135deg, #fd7e14, #ff8500);
        border-color: #fd7e14;
        color: white;
    }
    .court-advanced {
        background: linear-gradient(135deg, #dc3545, #c82333);
        border-color: #dc3545;
        color: white;
    }
    .skill-beginner {
        background-color: #28a745;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .skill-intermediate {
        background-color: #fd7e14;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .skill-advanced {
        background-color: #dc3545;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .simple-court-manager {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .court-item {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .court-info {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .court-actions {
        display: flex;
        gap: 0.5rem;
    }
    .quick-add-court {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .quick-add-court:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(40, 167, 69, 0.3);
    }
    .court-controls {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    .court-form {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin: 1rem 0;
    }
    .delete-btn {
        position: absolute;
        top: 5px;
        right: 5px;
        background: #dc3545;
        color: white;
        border: none;
        border-radius: 50%;
        width: 25px;
        height: 25px;
        font-size: 12px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .court-stats {
        display: flex;
        justify-content: space-around;
        background: linear-gradient(135deg, #74b9ff, #0984e3);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .stat-item {
        text-align: center;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
    }
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .admin-panel {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 2rem;
    }
    .stButton>button {
        background-color: #0d6efd;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #0b5ed7;
        transform: translateY(-2px);
    }
    .add-court-btn {
        background: linear-gradient(135deg, #28a745, #20c997) !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        color: white !important;
    }
    .save-layout-btn {
        background: linear-gradient(135deg, #007bff, #6610f2) !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.markdown("## Navigation")
page = st.sidebar.radio("Select Page", ["Home", "Court Layout", "Admin Panel"])

# Sidebar day selection (only show on Home page)
day = "Monday"  # Default value
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
            st.rerun()

# Main content area
st.markdown("<h1 class='header'>🏸 Team Baddies</h1>", unsafe_allow_html=True)

if page == "Home":
    # Create three columns: courts, player list, and input
    col1, col2, col3 = st.columns([2, 2, 1])
    
    # First column: Court Layout
    with col1:
        st.markdown("<div class='card'><h3>🏸 Court Layout</h3>", unsafe_allow_html=True)
        
        # Display courts in a simple grid with skill level colors
        active_courts = [c for c in court_layout["courts"] if c.get("active", True)]
        if active_courts:
            for i in range(0, len(active_courts), 2):
                cols = st.columns(2)
                for j in range(2):
                    if i + j < len(active_courts):
                        court = active_courts[i + j]
                        with cols[j]:
                            # Color mapping: beginner=green, intermediate=orange, advanced=red
                            st.markdown(
                                f"<div class='court court-{court['level']}'>"
                                f"<h4>{court['name']}</h4>"
                                f"<span class='skill-{court['level']}'>{court['level'].title()}</span>"
                                "</div>",
                                unsafe_allow_html=True
                            )
        else:
            st.info("No courts configured yet. Admin can add courts in the Court Layout page.")
        
        # Quick court management for admins
        if st.session_state.admin_logged_in:
            with st.expander("⚙️ Quick Court Management"):
                st.markdown("**Add a new court quickly:**")
                with st.form("quick_add_court"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        quick_name = st.text_input("Court Name", placeholder="e.g., Court 7")
                    with col_b:
                        quick_level = st.selectbox("Level", ["beginner", "intermediate", "advanced"])
                    
                    if st.form_submit_button("➕ Add Court"):
                        if quick_name:
                            new_id = max([c.get("id", 0) for c in court_layout["courts"]], default=0) + 1
                            # Find next available position
                            max_row = max([c.get("position", {}).get("row", 0) for c in court_layout["courts"]], default=-1)
                            new_court = {
                                "id": new_id,
                                "name": quick_name,
                                "level": quick_level,
                                "position": {"row": max_row + 1, "col": 0},
                                "active": True
                            }
                            court_layout["courts"].append(new_court)
                            save_data()
                            add_audit_log("Added Court", f"Quick add: {quick_name} ({quick_level})", "admin")
                            st.success(f"✅ {quick_name} added!")
                            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

    # Second column: Player Lists
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"<h3>Players for {day}</h3>", unsafe_allow_html=True)
        
        players = player_list[day]["Players"]
        waitlist = player_list[day]["Waitlist"]
        
        # Convert players list to DataFrame for better display
        if players:
            st.markdown("**Active Players:**")
            for i, player in enumerate(players, 1):
                skill_class = f"skill-{player[1].lower()}"
                st.markdown(
                    f"<div style='display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; margin: 0.25rem 0; background: #f8f9fa; border-radius: 5px;'>"
                    f"<span><strong>{i}.</strong> {player[0]}</span>"
                    f"<span class='{skill_class}'>{player[1]}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
        else:
            st.info("No players added yet.")
        
        st.markdown(f"<p style='color: #28a745; font-weight: bold;'>Player Count: {len(players)}/27</p>", unsafe_allow_html=True)
        
        st.markdown("<h3>Waitlist</h3>", unsafe_allow_html=True)
        if waitlist:
            st.markdown("**Waitlisted Players:**")
            for i, player in enumerate(waitlist, 1):
                skill_class = f"skill-{player[1].lower()}"
                st.markdown(
                    f"<div style='display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; margin: 0.25rem 0; background: #fff3cd; border-radius: 5px;'>"
                    f"<span><strong>{i}.</strong> {player[0]}</span>"
                    f"<span class='{skill_class}'>{player[1]}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
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
        st.warning("🔒 Please log in as admin to access the court layout settings.")
        st.info("💡 Use the admin login in the sidebar to continue.")
    else:
        st.markdown("<h2 style='text-align: center; color: #0d6efd; margin-bottom: 2rem;'>🏸 Court Management</h2>", unsafe_allow_html=True)
        
        # Court Statistics
        active_courts = [c for c in court_layout["courts"] if c.get("active", True)]
        total_courts = len(active_courts)
        beginner_courts = len([c for c in active_courts if c.get("level") == "beginner"])
        intermediate_courts = len([c for c in active_courts if c.get("level") == "intermediate"])
        advanced_courts = len([c for c in active_courts if c.get("level") == "advanced"])
        
        # Display stats
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🏸 Total Courts", total_courts)
        col2.metric("🟢 Beginner", beginner_courts)
        col3.metric("🟠 Intermediate", intermediate_courts)
        col4.metric("🔴 Advanced", advanced_courts)
        
        st.markdown("---")
        
        # Simple Add Court Section
        st.markdown("### ➕ Add New Court")
        with st.form("add_new_court", clear_on_submit=True):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                new_court_name = st.text_input("Court Name", placeholder="e.g., Court 7", help="Enter a unique name for the court")
            with col2:
                new_court_level = st.selectbox("Skill Level", 
                                             ["beginner", "intermediate", "advanced"],
                                             help="Choose the skill level for this court")
            with col3:
                if st.form_submit_button("➕ Add Court", type="primary", use_container_width=True):
                    if new_court_name:
                        # Check if court name already exists
                        existing_names = [c.get("name", "") for c in court_layout["courts"] if c.get("active", True)]
                        if new_court_name in existing_names:
                            st.error(f"❌ Court name '{new_court_name}' already exists!")
                        else:
                            new_id = max([c.get("id", 0) for c in court_layout["courts"]], default=0) + 1
                            # Simple positioning - just add to the end
                            max_row = max([c.get("position", {}).get("row", 0) for c in court_layout["courts"]], default=-1)
                            new_court = {
                                "id": new_id,
                                "name": new_court_name,
                                "level": new_court_level,
                                "position": {"row": max_row + 1, "col": 0},
                                "active": True
                            }
                            court_layout["courts"].append(new_court)
                            save_data()
                            add_audit_log("Added Court", f"New court '{new_court_name}' ({new_court_level})", "admin")
                            st.success(f"✅ Court '{new_court_name}' added successfully!")
                            st.rerun()
                    else:
                        st.error("❌ Please enter a court name!")
        
        st.markdown("---")
        
        # Existing Courts Management
        st.markdown("### 🏸 Existing Courts")
        
        if active_courts:
            for court in active_courts:
                with st.container():
                    st.markdown(f"""
                    <div class='court-item'>
                        <div class='court-info'>
                            <div class='court court-{court["level"]}' style='margin: 0; padding: 0.5rem; min-width: 120px;'>
                                <strong>{court["name"]}</strong>
                            </div>
                            <span class='skill-{court["level"]}' style='margin-left: 1rem;'>{court["level"].title()}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Action buttons for each court
                    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                    
                    with col1:
                        new_name = st.text_input(f"Name", value=court["name"], key=f"name_{court['id']}")
                        if new_name != court["name"]:
                            court["name"] = new_name
                    
                    with col2:
                        new_level = st.selectbox(f"Level", 
                                               ["beginner", "intermediate", "advanced"],
                                               index=["beginner", "intermediate", "advanced"].index(court["level"]),
                                               key=f"level_{court['id']}")
                        if new_level != court["level"]:
                            court["level"] = new_level
                    
                    with col3:
                        if st.button("�", key=f"save_{court['id']}", help="Save changes"):
                            save_data()
                            add_audit_log("Updated Court", f"Court '{court['name']}' updated", "admin")
                            st.success(f"✅ {court['name']} updated!")
                            st.rerun()
                    
                    with col4:
                        if st.button("🗑️", key=f"delete_{court['id']}", help="Delete court"):
                            court['active'] = False
                            save_data()
                            add_audit_log("Deleted Court", f"Court '{court['name']}' removed", "admin")
                            st.success(f"🗑️ {court['name']} deleted!")
                            st.rerun()
                    
                    st.markdown("---")
        else:
            st.info("🏸 No courts configured yet. Add your first court above!")
        
        # Quick Actions
        st.markdown("### ⚡ Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Save All Changes", type="primary", use_container_width=True):
                save_data()
                add_audit_log("Saved All Courts", "All court changes saved", "admin")
                st.success("✅ All changes saved!")
        
        with col2:
            if st.button("🔄 Reset to Default", use_container_width=True):
                if st.button("⚠️ Confirm Reset", key="confirm_reset", use_container_width=True):
                    court_layout["courts"] = [
                        {"id": 1, "level": "beginner", "name": "Court 1", "position": {"row": 0, "col": 0}, "active": True},
                        {"id": 2, "level": "beginner", "name": "Court 2", "position": {"row": 0, "col": 1}, "active": True},
                        {"id": 3, "level": "intermediate", "name": "Court 3", "position": {"row": 1, "col": 0}, "active": True},
                        {"id": 4, "level": "intermediate", "name": "Court 4", "position": {"row": 1, "col": 1}, "active": True},
                        {"id": 5, "level": "advanced", "name": "Court 5", "position": {"row": 2, "col": 0}, "active": True},
                        {"id": 6, "level": "advanced", "name": "Court 6", "position": {"row": 2, "col": 1}, "active": True}
                    ]
                    save_data()
                    st.success("🔄 Layout reset to default!")
                    st.rerun()
        
        with col3:
            # Export courts data
            if st.button("📥 Export Courts", use_container_width=True):
                courts_data = json.dumps(court_layout, indent=2)
                st.download_button(
                    label="💾 Download JSON",
                    data=courts_data,
                    file_name=f"courts_layout_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )

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
        total_waitlist = 0
        for day_key in player_list:
            total_waitlist += len(player_list[day_key]["Waitlist"])
        
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
