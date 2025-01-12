import streamlit as st
import json
from datetime import datetime

# Set up page config
st.set_page_config(page_title="Team Baddies", page_icon="🏸", layout="centered")

# Apply custom CSS for styling
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
        color: #333;
    }
    .header {
        text-align: center;
        color: #2a9d8f;
        font-size: 36px;
        font-weight: bold;
    }
    .subheader {
        text-align: center;
        color: #264653;
        font-size: 28px;
        font-weight: bold;
    }
    .title {
        text-align: center;
        font-size: 50px;
        color: #1d3557;
    }
    .input-container {
        display: flex;
        justify-content: space-between;
        margin-bottom: 20px;
    }
    .counter {
        font-weight: bold;
        font-size: 18px;
        color: #2a9d8f;
    }
    .player-list {
        font-size: 18px;
        color: #FFDD00;
        margin-left: 20px;
        font-weight: bold;
    }
    .audit-trail {
        font-size: 16px;
        color: #e76f51;
        margin-top: 30px;
    }
    .player-count {
        font-weight: bold;
        color: #264653;
    }
    
    /* Button Styling */
    .add-button {
        background-color: #4caf50; /* Solid Green */
        color: white; 
        font-size: 18px; 
        border-radius: 8px; 
        padding: 15px 30px; 
        width: 100%; 
        border: none; 
        cursor: pointer;
    }
    .remove-button {
        background-color: #e63946; /* Solid Red */
        color: white; 
        font-size: 18px; 
        border-radius: 8px; 
        padding: 15px 30px; 
        width: 100%; 
        border: none; 
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1 class='title'>🏸 Team Baddies</h1>", unsafe_allow_html=True)
st.markdown("<h2 class='subheader'>Badminton Roster Management</h2>", unsafe_allow_html=True)

# Helper function to save data
def save_data():
    with open("player_list.json", "w") as file:
        json.dump(player_list, file, indent=4)
    with open("audit_trail.json", "w") as file:
        json.dump(audit_trail, file, indent=4)

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

# Sidebar to select the day
day = st.sidebar.radio("Select a day:", ["Monday", "Tuesday", "Thursday"])

# Create two columns: one for the lists and one for the input
col1, col2 = st.columns([2, 1])

# Left column (col1) will display the player lists
with col1:
    # Display the player list
    st.markdown(f"### Players for {day}", unsafe_allow_html=True)
    players = player_list[day]["Players"]
    waitlist = player_list[day]["Waitlist"]
    if players:
        for idx, player in enumerate(players, 1):
            st.markdown(f"<p class='player-list'>{idx}. {player}</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p class='player-list'>No players added yet.</p>", unsafe_allow_html=True)

    # Display player count for the player list
    st.markdown(f"<p class='counter'>Player Count: {len(players)}/27</p>", unsafe_allow_html=True)

    # Display the waitlist
    st.markdown(f"### Waitlist for {day}", unsafe_allow_html=True)
    if waitlist:
        for idx, player in enumerate(waitlist, 1):
            st.markdown(f"<p class='player-list'>{idx}. {player}</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p class='player-list'>No players in waitlist.</p>", unsafe_allow_html=True)

    # Display player count for the waitlist
    st.markdown(f"<p class='counter'>Waitlist Count: {len(waitlist)}/20</p>", unsafe_allow_html=True)

# Right column (col2) will have the input and buttons
with col2:
    # Input for adding a new player
    st.markdown("<h3 class='subheader'>Add Player</h3>", unsafe_allow_html=True)
    new_player = st.text_input("Enter name to add to the list:")

    # Add player to list or waitlist based on availability
    if st.button("Add Player", key="add_player", use_container_width=True):
        if new_player:
            if len(players) < 27:
                players.append(new_player)
                st.success(f"{new_player} added to {day} player list!")
            elif len(waitlist) < 20:
                waitlist.append(new_player)
                st.success(f"{new_player} added to {day} waitlist!")
            else:
                st.error(f"Sorry, both the player list (27) and waitlist (20) are full for {day}.")
            
            # Record in the audit trail
            audit_trail.append({"action": "Added", "player": new_player, "day": day, "timestamp": datetime.now().isoformat()})
            save_data()

        else:
            st.error("Please enter a name before adding.")

    # Remove player from the player list or waitlist
    st.markdown("<h3 class='subheader'>Remove Player</h3>", unsafe_allow_html=True)

    # Allow user to remove from the player list
    remove_player = st.selectbox("Select a player to remove from the player list:", players + ["None"])
    if remove_player != "None":
        if st.button(f"Remove {remove_player} from {day} Player List", key="remove_player", use_container_width=True):
            players.remove(remove_player)
            st.success(f"Removed {remove_player} from the player list.")
            # Record in the audit trail
            audit_trail.append({"action": "Removed", "player": remove_player, "day": day, "timestamp": datetime.now().isoformat()})
            save_data()

    # Allow user to remove from the waitlist
    remove_waitlist_player = st.selectbox("Select a player to remove from the waitlist:", waitlist + ["None"])
    if remove_waitlist_player != "None":
        if st.button(f"Remove {remove_waitlist_player} from {day} Waitlist", key="remove_waitlist", use_container_width=True):
            waitlist.remove(remove_waitlist_player)
            st.success(f"Removed {remove_waitlist_player} from the waitlist.")
            # Record in the audit trail
            audit_trail.append({"action": "Removed", "player": remove_waitlist_player, "day": day, "timestamp": datetime.now().isoformat()})
            save_data()

# Display the audit trail for all users
st.markdown("<h3 class='subheader'>Audit Trail</h3>", unsafe_allow_html=True)
st.markdown("#### All player modifications are tracked here:")

# Show the audit trail as a readable markdown list
for entry in audit_trail:
    st.markdown(f"<p class='audit-trail'>{entry['timestamp']} - Action: {entry['action']} | Player: {entry['player']} | Day: {entry['day']}</p>", unsafe_allow_html=True)
