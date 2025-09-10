import streamlit as st
import json
from datetime import datetime
import pandas as pd
import hashlib
import uuid
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import io
import base64

# Set up page config
st.set_page_config(page_title="Team Baddies", page_icon="🏸", layout="wide")

# Initialize session state for admin login
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

# Admin credentials (in production, use environment variables or secure storage)
ADMIN_PASSWORD = "admin123"  # This should be hashed in production

# Helper functions
def generate_court_layout_image(courts, layout_settings):
    """Generate a visual court layout image using PIL"""
    # Image dimensions
    width = 1200
    height = 800
    
    # Colors for different skill levels
    colors = {
        'beginner': '#28a745',     # Green
        'intermediate': '#fd7e14', # Orange
        'advanced': '#dc3545',     # Red
        'background': '#f8f9fa',   # Light gray
        'border': '#343a40',       # Dark gray
        'text': '#ffffff'          # White
    }
    
    # Create image
    img = Image.new('RGB', (width, height), colors['background'])
    draw = ImageDraw.Draw(img)
    
    # Try to use a built-in font, fallback to default
    try:
        font_large = ImageFont.truetype("arial.ttf", 24)
        font_medium = ImageFont.truetype("arial.ttf", 18)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw title
    center_name = layout_settings.get('center_name', 'Team Baddies Badminton Center')
    title_bbox = draw.textbbox((0, 0), center_name, font=font_large)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(((width - title_width) // 2, 20), center_name, fill=colors['border'], font=font_large)
    
    # Calculate court layout
    rows = layout_settings.get('rows', 3)
    cols = layout_settings.get('cols', 4)
    
    # Court dimensions
    court_width = 160
    court_height = 100
    margin_x = (width - (cols * court_width + (cols - 1) * 20)) // 2
    margin_y = 80  # Start below title
    
    # Get active courts
    active_courts = [c for c in courts if c.get("active", True)]
    
    # Create a grid to track court positions
    court_grid = {}
    for court in active_courts:
        pos = court.get('position', {'row': 0, 'col': 0})
        row, col = pos.get('row', 0), pos.get('col', 0)
        if 0 <= row < rows and 0 <= col < cols:
            court_grid[(row, col)] = court
    
    # Draw courts
    for row in range(rows):
        for col in range(cols):
            # Calculate position
            x = margin_x + col * (court_width + 20)
            y = margin_y + row * (court_height + 30)
            
            if (row, col) in court_grid:
                court = court_grid[(row, col)]
                court_color = colors[court['level']]
                
                # Draw court rectangle with rounded corners effect
                draw.rectangle([x, y, x + court_width, y + court_height], 
                             fill=court_color, outline=colors['border'], width=3)
                
                # Draw badminton court lines (simplified)
                # Net line (center)
                net_y = y + court_height // 2
                draw.line([x + 10, net_y, x + court_width - 10, net_y], 
                         fill=colors['text'], width=2)
                
                # Service lines
                service_line_1 = y + court_height * 0.3
                service_line_2 = y + court_height * 0.7
                draw.line([x + 20, service_line_1, x + court_width - 20, service_line_1], 
                         fill=colors['text'], width=1)
                draw.line([x + 20, service_line_2, x + court_width - 20, service_line_2], 
                         fill=colors['text'], width=1)
                
                # Side lines
                draw.line([x + court_width // 2, y + 10, x + court_width // 2, y + court_height - 10], 
                         fill=colors['text'], width=1)
                
                # Court text
                court_name = court.get('name', f'Court {court.get("id", 1)}')
                court_level = court.get('level', 'beginner').title()
                
                # Get text dimensions for centering
                name_bbox = draw.textbbox((0, 0), court_name, font=font_medium)
                name_width = name_bbox[2] - name_bbox[0]
                level_bbox = draw.textbbox((0, 0), court_level, font=font_small)
                level_width = level_bbox[2] - level_bbox[0]
                
                # Draw text centered
                draw.text((x + (court_width - name_width) // 2, y + 25), 
                         court_name, fill=colors['text'], font=font_medium)
                draw.text((x + (court_width - level_width) // 2, y + 50), 
                         court_level, fill=colors['text'], font=font_small)
                
                # Court number in corner
                draw.text((x + 5, y + 5), str(court.get('id', '?')), 
                         fill=colors['text'], font=font_small)
                
            else:
                # Empty court space
                draw.rectangle([x, y, x + court_width, y + court_height], 
                             fill='#e9ecef', outline='#adb5bd', width=1)
                
                # Draw "+" for admin to add courts
                if 'admin_mode' in layout_settings and layout_settings['admin_mode']:
                    plus_size = 20
                    center_x = x + court_width // 2
                    center_y = y + court_height // 2
                    draw.line([center_x - plus_size, center_y, center_x + plus_size, center_y], 
                             fill='#6c757d', width=3)
                    draw.line([center_x, center_y - plus_size, center_x, center_y + plus_size], 
                             fill='#6c757d', width=3)
    
    # Add legend
    legend_y = height - 120
    legend_items = [
        ('Beginner', colors['beginner']),
        ('Intermediate', colors['intermediate']),
        ('Advanced', colors['advanced'])
    ]
    
    for i, (level, color) in enumerate(legend_items):
        legend_x = 50 + i * 200
        # Draw legend color box
        draw.rectangle([legend_x, legend_y, legend_x + 30, legend_y + 20], 
                      fill=color, outline=colors['border'], width=1)
        # Draw legend text
        draw.text((legend_x + 40, legend_y + 3), level, fill=colors['border'], font=font_medium)
    
    # Add statistics
    stats_y = legend_y + 40
    total_courts = len(active_courts)
    beginner_count = len([c for c in active_courts if c.get('level') == 'beginner'])
    intermediate_count = len([c for c in active_courts if c.get('level') == 'intermediate'])
    advanced_count = len([c for c in active_courts if c.get('level') == 'advanced'])
    
    stats_text = f"Total Courts: {total_courts} | Beginner: {beginner_count} | Intermediate: {intermediate_count} | Advanced: {advanced_count}"
    stats_bbox = draw.textbbox((0, 0), stats_text, font=font_small)
    stats_width = stats_bbox[2] - stats_bbox[0]
    draw.text(((width - stats_width) // 2, stats_y), stats_text, fill=colors['border'], font=font_small)
    
    return img

def save_court_layout_image(courts, layout_settings, filename="court_layout.png"):
    """Save the court layout image to a file"""
    img = generate_court_layout_image(courts, layout_settings)
    img.save(filename)
    return filename

def get_image_base64(img):
    """Convert PIL image to base64 string for display in Streamlit"""
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

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
            "center_name": "Team Baddies Badminton Center",
            "image_width": 1200,
            "image_height": 800,
            "court_style": "modern"
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
    .court-layout-container {
        background: linear-gradient(45deg, #f8f9fa, #e9ecef);
        border: 2px dashed #adb5bd;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        min-height: 300px;
        position: relative;
    }
    .court-layout-header {
        text-align: center;
        margin-bottom: 1.5rem;
        padding: 1rem;
        background: rgba(13, 110, 253, 0.1);
        border-radius: 10px;
    }
    .court-grid {
        display: grid;
        grid-template-columns: repeat(var(--grid-cols, 6), 1fr);
        grid-template-rows: repeat(var(--grid-rows, 4), 80px);
        gap: 0.5rem;
        margin: 1rem 0;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.8);
        border-radius: 10px;
    }
    .court-cell {
        border: 1px dashed #dee2e6;
        border-radius: 5px;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 80px;
        transition: all 0.3s ease;
        position: relative;
    }
    .court-cell:hover {
        background-color: rgba(13, 110, 253, 0.1);
        border-color: #0d6efd;
    }
    .court-positioned {
        cursor: grab;
        position: relative;
        border-radius: 8px;
        padding: 0.5rem;
        text-align: center;
        color: white;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        min-height: 60px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .court-positioned:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        cursor: move;
    }
    .court-size-small {
        font-size: 0.8rem;
        padding: 0.3rem;
        min-height: 50px;
    }
    .court-size-medium {
        font-size: 0.9rem;
        padding: 0.5rem;
        min-height: 70px;
    }
    .court-size-large {
        font-size: 1.1rem;
        padding: 0.7rem;
        min-height: 90px;
    }
    .court-controls-panel {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .grid-controls {
        display: flex;
        gap: 1rem;
        align-items: center;
        margin-bottom: 1rem;
        flex-wrap: wrap;
    }
    .empty-cell-btn {
        background: transparent;
        border: 2px dashed #adb5bd;
        border-radius: 5px;
        color: #6c757d;
        cursor: pointer;
        width: 100%;
        height: 100%;
        min-height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        transition: all 0.3s ease;
    }
    .empty-cell-btn:hover {
        background: rgba(13, 110, 253, 0.1);
        border-color: #0d6efd;
        color: #0d6efd;
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
    # Court Layout Section - Image-based visualization
    st.markdown("""
    <div class='court-layout-header'>
        <h3 style='margin: 0; color: #0d6efd;'>🏸 Badminton Center Layout</h3>
        <p style='margin: 0.5rem 0 0 0; color: #6c757d;'>Visual court layout and availability</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Generate and display court layout image
    try:
        layout_settings = court_layout.get("layout_settings", {})
        courts = court_layout.get("courts", [])
        
        # Generate the court layout image
        court_img = generate_court_layout_image(courts, layout_settings)
        
        # Display the image
        st.image(court_img, caption="Current Court Layout", use_column_width=True)
        
        # Quick court statistics
        active_courts = [c for c in courts if c.get("active", True)]
        total_courts = len(active_courts)
        beginner_courts = len([c for c in active_courts if c.get("level") == "beginner"])
        intermediate_courts = len([c for c in active_courts if c.get("level") == "intermediate"])
        advanced_courts = len([c for c in active_courts if c.get("level") == "advanced"])
        
        # Court stats in columns
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🏸 Total Courts", total_courts)
        col2.metric("🟢 Beginner", beginner_courts)
        col3.metric("🟠 Intermediate", intermediate_courts)
        col4.metric("🔴 Advanced", advanced_courts)
        
        # Live court status (placeholder for future booking system)
        with st.expander("📊 Live Court Status", expanded=False):
            st.info("🚧 Live booking system coming soon! Courts currently available for walk-ins.")
            
            # Display courts in a simple list format
            if active_courts:
                for court in active_courts:
                    col_a, col_b, col_c = st.columns([2, 1, 1])
                    with col_a:
                        skill_class = f"skill-{court['level']}"
                        st.markdown(f"""
                        <div style='display: flex; align-items: center; gap: 1rem;'>
                            <span class='{skill_class}' style='padding: 0.25rem 0.75rem; border-radius: 15px;'>{court['level'].title()}</span>
                            <strong>{court['name']}</strong>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_b:
                        st.success("✅ Available")
                    with col_c:
                        if st.session_state.admin_logged_in:
                            if st.button("⚙️", key=f"quick_edit_{court['id']}", help="Quick edit"):
                                st.session_state[f'editing_{court["id"]}'] = True
    
    except Exception as e:
        st.error(f"Error generating court layout: {str(e)}")
        st.info("💡 Please check the court layout settings in the Admin Panel.")
    
    st.markdown("---")
    
    # Player Registration Section - Below court layout
    st.markdown("### 👥 Player Registration")
    
    # Create two columns: player list and input
    col1, col2 = st.columns([3, 2])
    
    # First column: Player Lists
    with col1:
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
        
        st.markdown(f"<p style='color: #fd7e14; font-weight: bold;'>Waitlist Count: {len(waitlist)}/20</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Second column: Player Management
    with col2:
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
        
        st.markdown(f"<p style='color: #fd7e14; font-weight: bold;'>Waitlist Count: {len(waitlist)}/20</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# Court Layout Page
elif page == "Court Layout":
    if not st.session_state.admin_logged_in:
        st.warning("🔒 Please log in as admin to access the court layout settings.")
        st.info("💡 Use the admin login in the sidebar to continue.")
    else:
        st.markdown("<h2 style='text-align: center; color: #0d6efd; margin-bottom: 2rem;'>🏸 Court Layout Designer</h2>", unsafe_allow_html=True)
        
        # Layout Settings Section
        st.markdown("### ⚙️ Layout Settings")
        with st.container():
            col1, col2, col3 = st.columns(3)
            
            with col1:
                center_name = st.text_input("Center Name", 
                                          value=court_layout["layout_settings"].get("center_name", "Team Baddies Badminton Center"))
                court_layout["layout_settings"]["center_name"] = center_name
            
            with col2:
                rows = st.number_input("Grid Rows", min_value=2, max_value=8, 
                                     value=court_layout["layout_settings"].get("rows", 3))
                court_layout["layout_settings"]["rows"] = rows
            
            with col3:
                cols = st.number_input("Grid Columns", min_value=2, max_value=10, 
                                     value=court_layout["layout_settings"].get("cols", 4))
                court_layout["layout_settings"]["cols"] = cols
        
        # Generate and display preview
        st.markdown("### 🖼️ Layout Preview")
        try:
            layout_settings = court_layout.get("layout_settings", {})
            layout_settings["admin_mode"] = True  # Show + signs for empty positions
            courts = court_layout.get("courts", [])
            
            # Generate preview image
            preview_img = generate_court_layout_image(courts, layout_settings)
            st.image(preview_img, caption="Court Layout Preview", use_column_width=True)
            
            # Download button for the image
            img_buffer = io.BytesIO()
            preview_img.save(img_buffer, format='PNG')
            st.download_button(
                label="📥 Download Layout Image",
                data=img_buffer.getvalue(),
                file_name=f"court_layout_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                mime="image/png"
            )
            
        except Exception as e:
            st.error(f"Error generating preview: {str(e)}")
        
        st.markdown("---")
        
        # Court Management Section  
        st.markdown("### 🏸 Court Management")
        
        # Add new court section
        with st.expander("➕ Add New Court", expanded=False):
            with st.form("add_new_court_designer", clear_on_submit=True):
                add_cols = st.columns([2, 2, 1, 1])
                with add_cols[0]:
                    new_court_name = st.text_input("Court Name", placeholder="e.g., Court 7")
                with add_cols[1]:
                    new_court_level = st.selectbox("Skill Level", ["beginner", "intermediate", "advanced"])
                with add_cols[2]:
                    auto_position = st.checkbox("Auto Position", value=True, help="Automatically find next empty position")
                with add_cols[3]:
                    if st.form_submit_button("➕ Add", type="primary"):
                        if new_court_name:
                            # Check if court name already exists
                            existing_names = [c.get("name", "") for c in court_layout["courts"] if c.get("active", True)]
                            if new_court_name in existing_names:
                                st.error(f"❌ Court name '{new_court_name}' already exists!")
                            else:
                                new_id = max([c.get("id", 0) for c in court_layout["courts"]], default=0) + 1
                                
                                if auto_position:
                                    # Find next available position
                                    active_courts = [c for c in court_layout["courts"] if c.get("active", True)]
                                    used_positions = set()
                                    for court in active_courts:
                                        pos = court.get("position", {})
                                        used_positions.add((pos.get("row", 0), pos.get("col", 0)))
                                    
                                    # Find first available position
                                    found_position = False
                                    for r in range(rows):
                                        for c in range(cols):
                                            if (r, c) not in used_positions:
                                                new_court = {
                                                    "id": new_id,
                                                    "name": new_court_name,
                                                    "level": new_court_level,
                                                    "position": {"row": r, "col": c},
                                                    "active": True
                                                }
                                                court_layout["courts"].append(new_court)
                                                save_data()
                                                add_audit_log("Added Court", f"Designer: {new_court_name} ({new_court_level})", "admin")
                                                st.success(f"✅ {new_court_name} added at position ({r},{c})!")
                                                found_position = True
                                                st.rerun()
                                                break
                                        if found_position:
                                            break
                                    
                                    if not found_position:
                                        st.error("⚠️ No empty positions available. Increase grid size first.")
                                else:
                                    # Manual positioning (add at 0,0 for now)
                                    new_court = {
                                        "id": new_id,
                                        "name": new_court_name,
                                        "level": new_court_level,
                                        "position": {"row": 0, "col": 0},
                                        "active": True
                                    }
                                    court_layout["courts"].append(new_court)
                                    save_data()
                                    add_audit_log("Added Court", f"Designer: {new_court_name} ({new_court_level})", "admin")
                                    st.success(f"✅ {new_court_name} added! Position it using the grid below.")
                                    st.rerun()
                        else:
                            st.error("❌ Please enter a court name!")
        
        # Existing courts list
        active_courts = [c for c in court_layout["courts"] if c.get("active", True)]
        if active_courts:
            st.markdown("#### Edit Existing Courts")
            for court in active_courts:
                with st.container():
                    court_cols = st.columns([3, 2, 2, 1, 1])
                    
                    with court_cols[0]:
                        new_name = st.text_input("Name", value=court["name"], key=f"designer_name_{court['id']}")
                        if new_name != court["name"]:
                            court["name"] = new_name
                    
                    with court_cols[1]:
                        new_level = st.selectbox("Level", 
                                               ["beginner", "intermediate", "advanced"],
                                               index=["beginner", "intermediate", "advanced"].index(court["level"]),
                                               key=f"designer_level_{court['id']}")
                        if new_level != court["level"]:
                            court["level"] = new_level
                    
                    with court_cols[2]:
                        pos = court.get("position", {"row": 0, "col": 0})
                        st.text(f"Position: ({pos.get('row', 0)}, {pos.get('col', 0)})")
                    
                    with court_cols[3]:
                        if st.button("💾", key=f"designer_save_{court['id']}", help="Save changes"):
                            save_data()
                            add_audit_log("Updated Court", f"Designer: '{court['name']}' updated", "admin")
                            st.success(f"✅ {court['name']} updated!")
                            st.rerun()
                    
                    with court_cols[4]:
                        if st.button("🗑️", key=f"designer_delete_{court['id']}", help="Delete court"):
                            court['active'] = False
                            save_data()
                            add_audit_log("Deleted Court", f"Designer: '{court['name']}' removed", "admin")
                            st.success(f"🗑️ {court['name']} deleted!")
                            st.rerun()
                    
                    st.markdown("---")
        else:
            st.info("🏸 No courts configured yet. Add your first court above!")
        
        # Save all changes button
        st.markdown("### 💾 Save Layout")
        save_cols = st.columns(3)
        with save_cols[0]:
            if st.button("💾 Save All Changes", type="primary", use_container_width=True):
                save_data()
                add_audit_log("Saved Layout", "All court layout changes saved", "admin")
                st.success("✅ All changes saved!")
        
        with save_cols[1]:
            if st.button("🔄 Refresh Preview", use_container_width=True):
                st.rerun()
        
        with save_cols[2]:
            # Reset layout button
            if st.button("⚠️ Reset Layout", use_container_width=True):
                if st.button("⚠️ Confirm Reset", key="designer_confirm_reset", use_container_width=True):
                    court_layout["courts"] = [
                        {"id": 1, "level": "beginner", "name": "Court 1", "position": {"row": 0, "col": 0}, "active": True},
                        {"id": 2, "level": "beginner", "name": "Court 2", "position": {"row": 0, "col": 1}, "active": True},
                        {"id": 3, "level": "intermediate", "name": "Court 3", "position": {"row": 1, "col": 0}, "active": True},
                        {"id": 4, "level": "intermediate", "name": "Court 4", "position": {"row": 1, "col": 1}, "active": True},
                        {"id": 5, "level": "advanced", "name": "Court 5", "position": {"row": 2, "col": 0}, "active": True},
                        {"id": 6, "level": "advanced", "name": "Court 6", "position": {"row": 2, "col": 1}, "active": True}
                    ]
                    save_data()
                    add_audit_log("Reset Layout", "Layout reset to default courts", "admin")
                    st.success("🔄 Layout reset to default!")
                    st.rerun()
        
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
