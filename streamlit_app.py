import streamlit as st
import json
import pandas as pd
from datetime import datetime

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
            "center_name": "Team Baddies Badminton Center",
            "grid": [
                ["Court 1\n(Beginner)", "Court 2\n(Beginner)", "", ""],
                ["Court 3\n(Intermediate)", "Court 4\n(Intermediate)", "", ""],
                ["Court 5\n(Advanced)", "Court 6\n(Advanced)", "", ""]
            ]
        }
    
    try:
        with open("audit_trail.json", "r") as f:
            audit = json.load(f)
    except FileNotFoundError:
        audit = {"logs": []}
    
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
    """Add entry to audit log"""
    audit["logs"].append({
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details,
        "user_type": user_type
    })

# UI Functions
def render_css():
    """Apply custom CSS styling"""
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #1f4e79, #2e86ab);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-container {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f4e79;
    }
    </style>
    """, unsafe_allow_html=True)

def sidebar_navigation():
    """Render sidebar navigation"""
    st.sidebar.markdown("## 🏸 Navigation")
    
    pages = {
        "🏠 Home": "home",
        "📅 Monday": "monday", 
        "📅 Tuesday": "tuesday",
        "📅 Thursday": "thursday",
        "🏟️ Court Layout": "court_layout"
    }
    
    if st.session_state.admin_logged_in:
        pages["⚙️ Admin Panel"] = "admin"
    
    return st.sidebar.radio("Go to:", list(pages.keys()), format_func=lambda x: x)

def render_player_management(players, day, audit):
    """Render player management interface for a specific day"""
    st.markdown(f'<div class="main-header"><h1>🏸 {day} Training Session</h1></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 👥 Add New Player")
        with st.form(f"add_player_{day}"):
            name = st.text_input("Player Name")
            level = st.selectbox("Skill Level", ["Beginner", "Intermediate", "Advanced"])
            submitted = st.form_submit_button("Add Player")
            
            if submitted and name:
                new_player = {"name": name, "level": level, "timestamp": datetime.now().isoformat()}
                players[day]["Players"].append(new_player)
                add_audit_log(audit, f"Added Player - {day}", f"{name} ({level})")
                st.success(f"✅ {name} added to {day}!")
                st.rerun()
    
    with col2:
        st.markdown("### 📊 Quick Stats")
        total_players = len(players[day]["Players"])
        waitlist_count = len(players[day]["Waitlist"])
        st.metric("Total Players", total_players)
        st.metric("Waitlist", waitlist_count)
    
    # Display Players
    if players[day]["Players"]:
        st.markdown("### 🎾 Current Players")
        
        for i, player in enumerate(players[day]["Players"]):
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.write(f"**{player['name']}**")
            with col2:
                st.write(f"_{player['level']}_")
            with col3:
                if st.button("🗑️", key=f"remove_{day}_{i}", help="Remove player"):
                    removed_player = players[day]["Players"].pop(i)
                    add_audit_log(audit, f"Removed Player - {day}", f"{removed_player['name']}")
                    st.rerun()
    else:
        st.info(f"No players registered for {day} yet.")

def render_court_layout_page(courts, audit):
    """Render simplified court layout with editable dataframe"""
    st.markdown('<div class="main-header"><h1>🏟️ Court Layout Management</h1></div>', unsafe_allow_html=True)
    
    # Center Name Configuration
    st.markdown("### 🏢 Center Configuration")
    new_center_name = st.text_input("Center Name", value=courts.get("center_name", "Team Baddies Badminton Center"))
    
    if new_center_name != courts.get("center_name"):
        courts["center_name"] = new_center_name
        add_audit_log(audit, "Updated Center Name", new_center_name, "admin")
    
    st.markdown("---")
    
    # Court Grid Configuration
    st.markdown("### 🎯 Court Grid Layout")
    st.info("💡 **Instructions:** Edit the grid below to arrange your courts. Use format 'Court Name\\n(Level)' or leave empty for no court.")
    
    # Convert grid to DataFrame for editing
    df = pd.DataFrame(courts.get("grid", [["", "", "", ""], ["", "", "", ""], ["", "", "", ""]]))
    
    # Add row and column labels
    df.index = [f"Row {i+1}" for i in range(len(df))]
    df.columns = [f"Col {i+1}" for i in range(len(df.columns))]
    
    # Editable dataframe
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        key="court_grid_editor"
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save Layout", type="primary"):
            # Convert back to list format
            courts["grid"] = edited_df.values.tolist()
            add_audit_log(audit, "Updated Court Grid", "Court layout modified", "admin")
            st.success("✅ Court layout saved!")
            st.rerun()
    
    with col2:
        if st.button("🔄 Reset to Default"):
            courts["grid"] = [
                ["Court 1\n(Beginner)", "Court 2\n(Beginner)", "", ""],
                ["Court 3\n(Intermediate)", "Court 4\n(Intermediate)", "", ""],
                ["Court 5\n(Advanced)", "Court 6\n(Advanced)", "", ""]
            ]
            add_audit_log(audit, "Reset Court Grid", "Court layout reset to default", "admin")
            st.success("✅ Layout reset to default!")
            st.rerun()
    
    with col3:
        if st.button("➕ Add Row"):
            current_cols = len(courts.get("grid", [[]])[0]) if courts.get("grid") else 4
            courts["grid"].append([""] * current_cols)
            st.rerun()
    
    # Preview Section
    st.markdown("---")
    st.markdown("### 👀 Layout Preview")
    
    # Display current layout as a visual grid
    grid = courts.get("grid", [])
    if grid:
        st.markdown(f"**{courts.get('center_name', 'Court Layout')}**")
        
        for row_idx, row in enumerate(grid):
            cols = st.columns(len(row))
            for col_idx, cell in enumerate(row):
                with cols[col_idx]:
                    if cell.strip():
                        st.markdown(f"""
                        <div style="
                            border: 2px solid #1f4e79;
                            border-radius: 8px;
                            padding: 15px;
                            text-align: center;
                            background: #f0f8ff;
                            margin: 5px;
                            min-height: 80px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        ">
                            <div>{cell.replace(chr(10), '<br>')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="
                            border: 1px dashed #ccc;
                            border-radius: 8px;
                            padding: 15px;
                            text-align: center;
                            background: #f9f9f9;
                            margin: 5px;
                            min-height: 80px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            color: #999;
                        ">
                            Empty
                        </div>
                        """, unsafe_allow_html=True)

def render_admin_panel(players, courts, audit):
    """Render admin panel"""
    st.markdown('<div class="main-header"><h1>⚙️ Admin Panel</h1></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📊 Statistics", "📋 Audit Log", "🗑️ Data Management"])
    
    with tab1:
        st.markdown("### 📊 Overview Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_players = sum(len(players[day]["Players"]) for day in players)
            st.metric("Total Players", total_players)
        
        with col2:
            total_waitlist = sum(len(players[day]["Waitlist"]) for day in players)
            st.metric("Total Waitlist", total_waitlist)
        
        with col3:
            active_courts = sum(1 for row in courts.get("grid", []) for cell in row if cell.strip())
            st.metric("Active Courts", active_courts)
        
        # Players by day
        st.markdown("### 📅 Players by Day")
        for day in players:
            st.write(f"**{day}:** {len(players[day]['Players'])} players, {len(players[day]['Waitlist'])} waitlisted")
    
    with tab2:
        st.markdown("### 📋 Recent Activity")
        recent_logs = audit["logs"][-20:] if audit["logs"] else []
        
        if recent_logs:
            for log in reversed(recent_logs):
                st.write(f"**{log['timestamp'][:19]}** - {log['action']}: {log['details']} ({log['user_type']})")
        else:
            st.info("No audit logs available.")
    
    with tab3:
        st.markdown("### 🗑️ Data Management")
        st.warning("⚠️ These actions cannot be undone!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear All Players", help="Remove all players from all days"):
                for day in players:
                    players[day] = {"Players": [], "Waitlist": []}
                add_audit_log(audit, "Cleared All Players", "All player data cleared", "admin")
                st.success("✅ All players cleared!")
                st.rerun()
        
        with col2:
            if st.button("📊 Export Data", help="Download all data as JSON"):
                export_data = {
                    "players": players,
                    "courts": courts,
                    "audit": audit,
                    "exported_at": datetime.now().isoformat()
                }
                st.download_button(
                    label="📥 Download JSON",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"team_baddies_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

def main():
    """Main application function"""
    render_css()
    
    # Load data
    players, courts, audit = load_data()
    
    # Sidebar
    selected_page = sidebar_navigation()
    
    # Admin login in sidebar
    if not st.session_state.admin_logged_in:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🔐 Admin Login")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            if password == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                add_audit_log(audit, "Admin Login", "Admin logged in successfully", "admin")
                st.sidebar.success("✅ Logged in!")
                st.rerun()
            else:
                st.sidebar.error("❌ Invalid password")
    else:
        st.sidebar.success("✅ Admin logged in")
        if st.sidebar.button("Logout"):
            st.session_state.admin_logged_in = False
            add_audit_log(audit, "Admin Logout", "Admin logged out", "admin")
            st.rerun()
    
    # Main content routing
    if selected_page == "🏠 Home":
        st.markdown('<div class="main-header"><h1>🏸 Welcome to Team Baddies</h1></div>', unsafe_allow_html=True)
        
        st.markdown("### 📅 Training Schedule")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### Monday")
            st.info(f"👥 {len(players['Monday']['Players'])} players")
        
        with col2:
            st.markdown("#### Tuesday") 
            st.info(f"👥 {len(players['Tuesday']['Players'])} players")
        
        with col3:
            st.markdown("#### Thursday")
            st.info(f"👥 {len(players['Thursday']['Players'])} players")
        
        st.markdown("---")
        st.markdown("### 🏟️ Current Court Layout")
        st.markdown(f"**{courts.get('center_name', 'Team Baddies Badminton Center')}**")
        
        # Simple grid display for home page
        grid = courts.get("grid", [])
        if grid:
            for row in grid:
                cols = st.columns(len(row))
                for i, cell in enumerate(row):
                    if cell.strip():
                        cols[i].info(cell.replace('\n', ' '))
    
    elif selected_page in ["📅 Monday", "📅 Tuesday", "📅 Thursday"]:
        day = selected_page.split(" ")[1]
        render_player_management(players, day, audit)
    
    elif selected_page == "🏟️ Court Layout":
        if st.session_state.admin_logged_in:
            render_court_layout_page(courts, audit)
        else:
            st.warning("🔒 Admin access required for court layout management.")
            st.info("Please log in with admin credentials in the sidebar.")
    
    elif selected_page == "⚙️ Admin Panel":
        render_admin_panel(players, courts, audit)
    
    # Save data
    save_data(players, courts, audit)

if __name__ == "__main__":
    main()
