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
        background: linear-gradient(135deg, #a8e6cf, #88d8a3);
        border-color: #52b788;
    }
    .court-intermediate {
        background: linear-gradient(135deg, #ffd60a, #ffbe0b);
        border-color: #fb8500;
    }
    .court-advanced {
        background: linear-gradient(135deg, #f72585, #b5179e);
        border-color: #7209b7;
        color: white;
    }
    .court-layout-grid {
        background: linear-gradient(45deg, #e9ecef, #f8f9fa);
        border: 2px dashed #adb5bd;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        min-height: 400px;
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        position: relative;
    }
    .court-layout-grid::before {
        content: "🏸 Badminton Center Layout";
        position: absolute;
        top: 10px;
        left: 20px;
        font-size: 1.2rem;
        font-weight: bold;
        color: #495057;
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
        st.warning("🔒 Please log in as admin to access the court layout settings.")
        st.info("💡 Use the admin login in the sidebar to continue.")
    else:
        st.markdown("<h2 style='text-align: center; color: #0d6efd; margin-bottom: 2rem;'>🏸 Court Layout Management</h2>", unsafe_allow_html=True)
        
        # Initialize session state for court management
        if 'editing_court' not in st.session_state:
            st.session_state.editing_court = None
        if 'show_add_form' not in st.session_state:
            st.session_state.show_add_form = False
        
        # Court Statistics
        total_courts = len([c for c in court_layout["courts"] if c.get("active", True)])
        beginner_courts = len([c for c in court_layout["courts"] if c.get("level") == "beginner" and c.get("active", True)])
        intermediate_courts = len([c for c in court_layout["courts"] if c.get("level") == "intermediate" and c.get("active", True)])
        advanced_courts = len([c for c in court_layout["courts"] if c.get("level") == "advanced" and c.get("active", True)])
        
        st.markdown(f"""
        <div class='court-stats'>
            <div class='stat-item'>
                <div class='stat-number'>{total_courts}</div>
                <div class='stat-label'>Total Courts</div>
            </div>
            <div class='stat-item'>
                <div class='stat-number'>{beginner_courts}</div>
                <div class='stat-label'>Beginner</div>
            </div>
            <div class='stat-item'>
                <div class='stat-number'>{intermediate_courts}</div>
                <div class='stat-label'>Intermediate</div>
            </div>
            <div class='stat-item'>
                <div class='stat-number'>{advanced_courts}</div>
                <div class='stat-label'>Advanced</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Court Controls
        st.markdown("""
        <div class='court-controls'>
            <h3 style='margin-top: 0; color: white;'>⚙️ Court Management Controls</h3>
            <p style='margin-bottom: 0; opacity: 0.9;'>Add new courts, modify existing ones, or rearrange the layout</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Control buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("➕ Add New Court", key="add_court", help="Add a new court to the layout"):
                st.session_state.show_add_form = True
                st.session_state.editing_court = None
        
        with col2:
            if st.button("💾 Save Layout", key="save_layout", help="Save all changes to the court layout"):
                save_data()
                add_audit_log("Updated Court Layout", "Complete court layout saved", "admin")
                st.success("✅ Court layout saved successfully!")
        
        with col3:
            if st.button("🔄 Reset Layout", key="reset_layout", help="Reset to default layout"):
                if st.button("⚠️ Confirm Reset", key="confirm_reset"):
                    court_layout["courts"] = [
                        {"id": 1, "level": "beginner", "name": "Court 1", "position": {"row": 0, "col": 0}, "active": True},
                        {"id": 2, "level": "beginner", "name": "Court 2", "position": {"row": 0, "col": 1}, "active": True},
                        {"id": 3, "level": "intermediate", "name": "Court 3", "position": {"row": 1, "col": 0}, "active": True},
                        {"id": 4, "level": "intermediate", "name": "Court 4", "position": {"row": 1, "col": 1}, "active": True},
                        {"id": 5, "level": "advanced", "name": "Court 5", "position": {"row": 2, "col": 0}, "active": True},
                        {"id": 6, "level": "advanced", "name": "Court 6", "position": {"row": 2, "col": 1}, "active": True}
                    ]
                    save_data()
                    st.success("Layout reset to default!")
                    st.rerun()
        
        with col4:
            center_name = st.text_input("🏟️ Center Name", 
                                      value=court_layout.get("layout_settings", {}).get("center_name", "Badminton Center"),
                                      help="Name of your badminton center")
            if center_name != court_layout.get("layout_settings", {}).get("center_name", "Badminton Center"):
                if "layout_settings" not in court_layout:
                    court_layout["layout_settings"] = {}
                court_layout["layout_settings"]["center_name"] = center_name
        
        # Add New Court Form
        if st.session_state.show_add_form:
            st.markdown("""
            <div class='court-form'>
                <h4>🆕 Add New Court</h4>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("add_court_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_court_name = st.text_input("Court Name", placeholder="e.g., Court 7")
                    new_court_level = st.selectbox("Skill Level", ["beginner", "intermediate", "advanced"])
                with col2:
                    new_court_row = st.number_input("Row Position", min_value=0, max_value=10, value=0)
                    new_court_col = st.number_input("Column Position", min_value=0, max_value=10, value=0)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("✅ Add Court", type="primary"):
                        new_id = max([c.get("id", 0) for c in court_layout["courts"]], default=0) + 1
                        new_court = {
                            "id": new_id,
                            "name": new_court_name,
                            "level": new_court_level,
                            "position": {"row": new_court_row, "col": new_court_col},
                            "active": True
                        }
                        court_layout["courts"].append(new_court)
                        st.session_state.show_add_form = False
                        add_audit_log("Added Court", f"New court '{new_court_name}' added", "admin")
                        st.success(f"✅ Court '{new_court_name}' added successfully!")
                        st.rerun()
                
                with col2:
                    if st.form_submit_button("❌ Cancel"):
                        st.session_state.show_add_form = False
                        st.rerun()
        
        # Court Layout Grid
        st.markdown(f"""
        <div style='text-align: center; margin: 2rem 0;'>
            <h3>🗺️ {court_layout.get("layout_settings", {}).get("center_name", "Badminton Center")} Layout</h3>
            <p style='color: #6c757d;'>Click on courts to edit them</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create a grid layout for courts
        max_row = max([c.get("position", {}).get("row", 0) for c in court_layout["courts"]], default=2) + 1
        max_col = max([c.get("position", {}).get("col", 0) for c in court_layout["courts"]], default=3) + 1
        
        # Display courts in grid layout
        for row in range(max_row):
            cols = st.columns(max_col)
            for col in range(max_col):
                # Find court at this position
                court_at_position = None
                for court in court_layout["courts"]:
                    if (court.get("position", {}).get("row") == row and 
                        court.get("position", {}).get("col") == col and 
                        court.get("active", True)):
                        court_at_position = court
                        break
                
                with cols[col]:
                    if court_at_position:
                        # Display court
                        court_html = f"""
                        <div class='court court-{court_at_position["level"]}' style='position: relative;'>
                            <div style='font-weight: bold; font-size: 1.1rem;'>{court_at_position["name"]}</div>
                            <div style='font-size: 0.9rem; opacity: 0.8;'>{court_at_position["level"].title()}</div>
                            <div style='font-size: 0.8rem; margin-top: 5px;'>🏸</div>
                        </div>
                        """
                        st.markdown(court_html, unsafe_allow_html=True)
                        
                        # Court action buttons
                        court_col1, court_col2 = st.columns(2)
                        with court_col1:
                            if st.button("✏️", key=f"edit_{court_at_position['id']}", help="Edit court"):
                                st.session_state.editing_court = court_at_position['id']
                                st.session_state.show_add_form = False
                        with court_col2:
                            if st.button("🗑️", key=f"delete_{court_at_position['id']}", help="Delete court"):
                                court_at_position['active'] = False
                                add_audit_log("Deleted Court", f"Court '{court_at_position['name']}' removed", "admin")
                                st.success(f"Court '{court_at_position['name']}' removed!")
                                st.rerun()
                    else:
                        # Empty space - show add button
                        if st.button("➕", key=f"add_at_{row}_{col}", help=f"Add court at position {row},{col}"):
                            st.session_state.show_add_form = True
                            st.session_state.editing_court = None
        
        # Edit Court Form
        if st.session_state.editing_court:
            editing_court = next((c for c in court_layout["courts"] if c["id"] == st.session_state.editing_court), None)
            if editing_court:
                st.markdown(f"""
                <div class='court-form'>
                    <h4>✏️ Edit Court: {editing_court['name']}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                with st.form("edit_court_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        edit_name = st.text_input("Court Name", value=editing_court["name"])
                        edit_level = st.selectbox("Skill Level", 
                                                ["beginner", "intermediate", "advanced"],
                                                index=["beginner", "intermediate", "advanced"].index(editing_court["level"]))
                    with col2:
                        edit_row = st.number_input("Row Position", 
                                                 min_value=0, max_value=10, 
                                                 value=editing_court.get("position", {}).get("row", 0))
                        edit_col = st.number_input("Column Position", 
                                                 min_value=0, max_value=10, 
                                                 value=editing_court.get("position", {}).get("col", 0))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Save Changes", type="primary"):
                            editing_court["name"] = edit_name
                            editing_court["level"] = edit_level
                            editing_court["position"] = {"row": edit_row, "col": edit_col}
                            st.session_state.editing_court = None
                            add_audit_log("Edited Court", f"Court '{edit_name}' updated", "admin")
                            st.success(f"✅ Court '{edit_name}' updated successfully!")
                            st.rerun()
                    
                    with col2:
                        if st.form_submit_button("❌ Cancel"):
                            st.session_state.editing_court = None
                            st.rerun()
        
        # Layout Settings
        with st.expander("⚙️ Advanced Layout Settings"):
            st.markdown("### Grid Dimensions")
            col1, col2 = st.columns(2)
            with col1:
                if "layout_settings" not in court_layout:
                    court_layout["layout_settings"] = {"rows": 3, "cols": 4}
                
                new_rows = st.slider("Number of Rows", 1, 10, 
                                   value=court_layout.get("layout_settings", {}).get("rows", 3))
                court_layout["layout_settings"]["rows"] = new_rows
            
            with col2:
                new_cols = st.slider("Number of Columns", 1, 10, 
                                   value=court_layout.get("layout_settings", {}).get("cols", 4))
                court_layout["layout_settings"]["cols"] = new_cols
            
            st.markdown("### Export/Import Layout")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Export Layout"):
                    layout_json = json.dumps(court_layout, indent=2)
                    st.download_button(
                        label="💾 Download Layout JSON",
                        data=layout_json,
                        file_name="court_layout.json",
                        mime="application/json"
                    )
            
            with col2:
                uploaded_file = st.file_uploader("📤 Import Layout", type=['json'])
                if uploaded_file is not None:
                    try:
                        imported_layout = json.load(uploaded_file)
                        court_layout.update(imported_layout)
                        st.success("Layout imported successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error importing layout: {e}")

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
