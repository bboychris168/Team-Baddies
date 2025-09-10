import streamlit as st
import json
from datetime import datetime
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import platform

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
                "image_width": 1200, "image_height": 800, "court_style": "modern"
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
def generate_court_image(courts, settings):
    """Generate court layout image"""
    width, height = 1200, 800
    colors = {
        'beginner': '#28a745', 'intermediate': '#fd7e14', 'advanced': '#dc3545',
        'background': '#f8f9fa', 'border': '#343a40', 'text': '#ffffff'
    }
    
    img = Image.new('RGB', (width, height), colors['background'])
    draw = ImageDraw.Draw(img)
    
    # Load fonts with fallback
    try:
        if platform.system() == "Windows":
            font_lg = ImageFont.truetype("arial.ttf", 24)
            font_md = ImageFont.truetype("arial.ttf", 18)
            font_sm = ImageFont.truetype("arial.ttf", 14)
        else:
            font_lg = ImageFont.truetype("DejaVuSans.ttf", 24)
            font_md = ImageFont.truetype("DejaVuSans.ttf", 18)
            font_sm = ImageFont.truetype("DejaVuSans.ttf", 14)
    except:
        font_lg = font_md = font_sm = None
    
    # Draw title
    title = settings.get('center_name', 'Team Baddies Badminton Center')
    try:
        if font_lg:
            bbox = draw.textbbox((0, 0), title, font=font_lg)
            x = (width - (bbox[2] - bbox[0])) // 2
            draw.text((x, 20), title, fill=colors['border'], font=font_lg)
        else:
            draw.text((width//2 - len(title)*6, 20), title, fill=colors['border'])
    except:
        draw.text((50, 20), title, fill=colors['border'])
    
    # Court layout
    rows, cols = settings.get('rows', 3), settings.get('cols', 4)
    court_w, court_h = 160, 100
    margin_x = (width - (cols * court_w + (cols-1) * 20)) // 2
    margin_y = 80
    
    active_courts = [c for c in courts if c.get("active", True)]
    court_positions = {(c.get('position', {}).get('row', 0), c.get('position', {}).get('col', 0)): c 
                      for c in active_courts}
    
    # Draw courts
    for row in range(rows):
        for col in range(cols):
            x = margin_x + col * (court_w + 20)
            y = margin_y + row * (court_h + 30)
            
            if (row, col) in court_positions:
                court = court_positions[(row, col)]
                color = colors[court['level']]
                
                # Draw court rectangle
                draw.rectangle([x, y, x + court_w, y + court_h], fill=color, outline=colors['border'], width=3)
                
                # Draw badminton lines
                net_y = y + court_h // 2
                draw.line([x + 10, net_y, x + court_w - 10, net_y], fill=colors['text'], width=2)
                draw.line([x + 20, y + court_h * 0.3, x + court_w - 20, y + court_h * 0.3], fill=colors['text'], width=1)
                draw.line([x + 20, y + court_h * 0.7, x + court_w - 20, y + court_h * 0.7], fill=colors['text'], width=1)
                draw.line([x + court_w // 2, y + 10, x + court_w // 2, y + court_h - 10], fill=colors['text'], width=1)
                
                # Draw text
                name = court.get('name', f'Court {court.get("id", 1)}')
                level = court.get('level', 'beginner').title()
                
                try:
                    if font_md and font_sm:
                        name_bbox = draw.textbbox((0, 0), name, font=font_md)
                        level_bbox = draw.textbbox((0, 0), level, font=font_sm)
                        draw.text((x + (court_w - (name_bbox[2] - name_bbox[0])) // 2, y + 25), name, fill=colors['text'], font=font_md)
                        draw.text((x + (court_w - (level_bbox[2] - level_bbox[0])) // 2, y + 50), level, fill=colors['text'], font=font_sm)
                        draw.text((x + 5, y + 5), str(court.get('id', '?')), fill=colors['text'], font=font_sm)
                    else:
                        draw.text((x + 40, y + 25), name, fill=colors['text'])
                        draw.text((x + 40, y + 50), level, fill=colors['text'])
                        draw.text((x + 5, y + 5), str(court.get('id', '?')), fill=colors['text'])
                except:
                    draw.text((x + 20, y + 30), name, fill=colors['text'])
                    draw.text((x + 20, y + 50), level, fill=colors['text'])
            else:
                # Empty space
                draw.rectangle([x, y, x + court_w, y + court_h], fill='#e9ecef', outline='#adb5bd', width=1)
                if settings.get('admin_mode'):
                    draw.line([x + court_w//2 - 20, y + court_h//2, x + court_w//2 + 20, y + court_h//2], fill='#6c757d', width=3)
                    draw.line([x + court_w//2, y + court_h//2 - 20, x + court_w//2, y + court_h//2 + 20], fill='#6c757d', width=3)
    
    # Legend
    legend_y = height - 120
    legend_items = [('Beginner', colors['beginner']), ('Intermediate', colors['intermediate']), ('Advanced', colors['advanced'])]
    
    for i, (level, color) in enumerate(legend_items):
        x = 50 + i * 200
        draw.rectangle([x, legend_y, x + 30, legend_y + 20], fill=color, outline=colors['border'], width=1)
        try:
            if font_md:
                draw.text((x + 40, legend_y + 3), level, fill=colors['border'], font=font_md)
            else:
                draw.text((x + 40, legend_y + 3), level, fill=colors['border'])
        except:
            draw.text((x + 40, legend_y + 3), level, fill=colors['border'])
    
    # Statistics
    stats = f"Total: {len(active_courts)} | " + " | ".join([f"{level.title()}: {len([c for c in active_courts if c.get('level') == level])}" 
                                                           for level in ['beginner', 'intermediate', 'advanced']])
    try:
        if font_sm:
            bbox = draw.textbbox((0, 0), stats, font=font_sm)
            x = (width - (bbox[2] - bbox[0])) // 2
            draw.text((x, legend_y + 40), stats, fill=colors['border'], font=font_sm)
        else:
            draw.text((width//2 - len(stats)*4, legend_y + 40), stats, fill=colors['border'])
    except:
        draw.text((50, legend_y + 40), stats, fill=colors['border'])
    
    return img

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
    page = st.sidebar.radio("Select Page", ["Home", "Court Layout", "Admin Panel"])
    
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

def render_player_management(players, day, audit):
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
        
        new_player = st.text_input("Name:")
        skill_level = st.selectbox("Skill Level:", ["Beginner", "Intermediate", "Advanced"])
        
        if st.button("Add Player", use_container_width=True):
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
                st.rerun()
            else:
                st.error("Please enter a name.")
        
        st.markdown("<h3>Remove Player</h3>", unsafe_allow_html=True)
        
        # Remove from player list
        if player_list:
            remove_player = st.selectbox("From player list:", ["None"] + [p[0] for p in player_list])
            if remove_player != "None" and st.button("Remove from List"):
                player_data = next(p for p in player_list if p[0] == remove_player)
                player_list.remove(player_data)
                add_audit_log(audit, "Removed", f"{remove_player} from {day} list")
                st.success(f"Removed {remove_player}")
                st.rerun()
        
        # Remove from waitlist
        if waitlist:
            remove_waitlist = st.selectbox("From waitlist:", ["None"] + [p[0] for p in waitlist])
            if remove_waitlist != "None" and st.button("Remove from Waitlist"):
                player_data = next(p for p in waitlist if p[0] == remove_waitlist)
                waitlist.remove(player_data)
                add_audit_log(audit, "Removed", f"{remove_waitlist} from {day} waitlist")
                st.success(f"Removed {remove_waitlist}")
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

def render_court_layout_page(courts, audit):
    """Render court layout management page"""
    if not st.session_state.admin_logged_in:
        st.warning("🔒 Please log in as admin to access court layout settings.")
        return
    
    st.markdown("<h2 style='text-align: center; color: #0d6efd; margin-bottom: 2rem;'>🏸 Court Layout Designer</h2>", unsafe_allow_html=True)
    
    # Ensure layout_settings exists
    if "layout_settings" not in courts:
        courts["layout_settings"] = {
            "rows": 3, "cols": 4, "center_name": "Team Baddies Badminton Center",
            "image_width": 1200, "image_height": 800, "court_style": "modern"
        }
    
    # Layout settings
    st.markdown("### ⚙️ Layout Settings")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        center_name = st.text_input("Center Name", value=courts["layout_settings"].get("center_name", "Team Baddies Badminton Center"))
        courts["layout_settings"]["center_name"] = center_name
    
    with col2:
        rows = st.number_input("Grid Rows", min_value=2, max_value=8, value=courts["layout_settings"].get("rows", 3))
        courts["layout_settings"]["rows"] = rows
    
    with col3:
        cols = st.number_input("Grid Columns", min_value=2, max_value=10, value=courts["layout_settings"].get("cols", 4))
        courts["layout_settings"]["cols"] = cols
    
    # Generate preview
    st.markdown("### 🖼️ Layout Preview")
    try:
        settings = courts.get("layout_settings", {})
        settings["admin_mode"] = True
        court_list = courts.get("courts", [])
        
        preview_img = generate_court_image(court_list, settings)
        st.image(preview_img, caption="Court Layout Preview", use_container_width=True)
        
        # Download button
        img_buffer = io.BytesIO()
        preview_img.save(img_buffer, format='PNG')
        st.download_button("📥 Download Layout Image", data=img_buffer.getvalue(),
                          file_name=f"court_layout_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png", mime="image/png")
    except Exception as e:
        st.error(f"Error generating preview: {str(e)}")
    
    # Court management
    st.markdown("---\n### 🏸 Court Management")
    
    # Add new court
    with st.expander("➕ Add New Court"):
        with st.form("add_court", clear_on_submit=True):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                new_name = st.text_input("Court Name", placeholder="e.g., Court 7")
            with col2:
                new_level = st.selectbox("Skill Level", ["beginner", "intermediate", "advanced"])
            with col3:
                if st.form_submit_button("➕ Add", type="primary"):
                    if new_name:
                        active_courts = [c for c in courts["courts"] if c.get("active", True)]
                        existing_names = [c.get("name", "") for c in active_courts]
                        if new_name in existing_names:
                            st.error(f"❌ Court name '{new_name}' already exists!")
                        else:
                            new_id = max([c.get("id", 0) for c in courts["courts"]], default=0) + 1
                            # Find next available position
                            used_positions = {(c.get("position", {}).get("row", 0), c.get("position", {}).get("col", 0)) 
                                            for c in active_courts}
                            
                            found = False
                            for r in range(rows):
                                for c in range(cols):
                                    if (r, c) not in used_positions:
                                        courts["courts"].append({
                                            "id": new_id, "name": new_name, "level": new_level,
                                            "position": {"row": r, "col": c}, "active": True
                                        })
                                        add_audit_log(audit, "Added Court", f"{new_name} ({new_level})", "admin")
                                        st.success(f"✅ {new_name} added!")
                                        found = True
                                        st.rerun()
                                        break
                                if found:
                                    break
                            if not found:
                                st.error("⚠️ No empty positions available.")
                    else:
                        st.error("❌ Please enter a court name!")
    
    # List existing courts
    active_courts = [c for c in courts["courts"] if c.get("active", True)]
    if active_courts:
        st.markdown("#### Edit Courts")
        for court in active_courts:
            cols = st.columns([3, 2, 2, 1, 1])
            
            with cols[0]:
                new_name = st.text_input("Name", value=court["name"], key=f"name_{court['id']}")
                if new_name != court["name"]:
                    court["name"] = new_name
            
            with cols[1]:
                levels = ["beginner", "intermediate", "advanced"]
                new_level = st.selectbox("Level", levels, index=levels.index(court["level"]), key=f"level_{court['id']}")
                if new_level != court["level"]:
                    court["level"] = new_level
            
            with cols[2]:
                pos = court.get("position", {"row": 0, "col": 0})
                st.text(f"Position: ({pos.get('row', 0)}, {pos.get('col', 0)})")
            
            with cols[3]:
                if st.button("💾", key=f"save_{court['id']}", help="Save"):
                    add_audit_log(audit, "Updated Court", f"'{court['name']}' updated", "admin")
                    st.success(f"✅ {court['name']} updated!")
                    st.rerun()
            
            with cols[4]:
                if st.button("🗑️", key=f"delete_{court['id']}", help="Delete"):
                    court['active'] = False
                    add_audit_log(audit, "Deleted Court", f"'{court['name']}' removed", "admin")
                    st.success(f"🗑️ {court['name']} deleted!")
                    st.rerun()
            
            st.markdown("---")
    else:
        st.info("🏸 No courts configured yet.")

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
        # Court layout image
        st.markdown("### 🏸 Badminton Center Layout")
        try:
            settings = courts.get("layout_settings", {})
            court_list = courts.get("courts", [])
            court_img = generate_court_image(court_list, settings)
            st.image(court_img, caption="Current Court Layout", use_container_width=True)
            
            # Quick stats
            active_courts = [c for c in court_list if c.get("active", True)]
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("🏸 Total Courts", len(active_courts))
            col2.metric("🟢 Beginner", len([c for c in active_courts if c.get("level") == "beginner"]))
            col3.metric("🟠 Intermediate", len([c for c in active_courts if c.get("level") == "intermediate"]))
            col4.metric("🔴 Advanced", len([c for c in active_courts if c.get("level") == "advanced"]))
        except Exception as e:
            st.error(f"Error generating court layout: {str(e)}")
        
        st.markdown("---")
        
        # Player management
        st.markdown("### 👥 Player Registration")
        render_player_management(players, day, audit)
    
    elif page == "Court Layout":
        render_court_layout_page(courts, audit)
    
    elif page == "Admin Panel":
        render_admin_panel(players, courts, audit)
    
    # Save data
    save_data(players, courts, audit)

if __name__ == "__main__":
    main()
