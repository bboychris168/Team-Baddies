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
            "total_courts": 6, "image_width": 1200, "image_height": 800
        }
    
    # Initialize courts list if needed
    if "courts" not in courts:
        courts["courts"] = []
    
    # Step 1: Basic Settings
    st.markdown("### 📊 Step 1: Basic Configuration")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        center_name = st.text_input("🏢 Center Name", 
                                   value=courts["layout_settings"].get("center_name", "Team Baddies Badminton Center"))
        courts["layout_settings"]["center_name"] = center_name
    
    with col2:
        total_courts = st.number_input("🏸 Total Number of Courts", 
                                     min_value=1, max_value=50, 
                                     value=courts["layout_settings"].get("total_courts", 6))
        courts["layout_settings"]["total_courts"] = total_courts
    
    with col3:
        if st.button("🔄 Reset All Courts", help="This will clear all court configurations"):
            courts["courts"] = []
            add_audit_log(audit, "Reset Courts", "All courts cleared", "admin")
            st.success("✅ All courts reset!")
            st.rerun()
    
    # Step 2: Grid Layout Configuration
    st.markdown("---")
    st.markdown("### 🎯 Step 2: Grid Layout Configuration")
    
    grid_col1, grid_col2, grid_col3 = st.columns(3)
    
    with grid_col1:
        rows = st.number_input("📏 Grid Rows", min_value=1, max_value=10, 
                              value=courts["layout_settings"].get("rows", 3))
        courts["layout_settings"]["rows"] = rows
    
    with grid_col2:
        cols = st.number_input("📐 Grid Columns", min_value=1, max_value=10, 
                              value=courts["layout_settings"].get("cols", 4))
        courts["layout_settings"]["cols"] = cols
    
    with grid_col3:
        max_positions = rows * cols
        st.metric("📋 Available Positions", max_positions)
        if total_courts > max_positions:
            st.error(f"⚠️ {total_courts} courts won't fit in {rows}x{cols} grid!")
    
    # Step 3: Court Assignment Grid
    st.markdown("---")
    st.markdown("### 🏸 Step 3: Assign Courts to Grid Positions")
    
    # Create a grid for court assignment
    court_assignments = {}
    
    # Get existing court assignments
    for court in courts.get("courts", []):
        if court.get("active", True):
            pos = court.get("position", {})
            row, col = pos.get("row", 0), pos.get("col", 0)
            court_assignments[(row, col)] = {
                "id": court.get("id"),
                "name": court.get("name", ""),
                "level": court.get("level", "beginner")
            }
    
    # Display grid for court assignment
    assigned_courts = 0
    for row in range(rows):
        st.markdown(f"**Row {row + 1}:**")
        grid_cols = st.columns(cols)
        
        for col in range(cols):
            with grid_cols[col]:
                position_key = f"pos_{row}_{col}"
                current_assignment = court_assignments.get((row, col), {})
                
                st.markdown(f"**Position ({row+1}, {col+1})**")
                
                # Court assignment form
                with st.container():
                    # Check if position is assigned
                    is_assigned = (row, col) in court_assignments
                    
                    if is_assigned:
                        assigned_courts += 1
                        st.success(f"✅ {current_assignment['name']}")
                        st.markdown(f"Level: **{current_assignment['level'].title()}**")
                        
                        # Edit/Remove buttons
                        edit_col, remove_col = st.columns(2)
                        with edit_col:
                            if st.button("✏️", key=f"edit_{row}_{col}", help="Edit court"):
                                st.session_state[f"editing_{row}_{col}"] = True
                                st.rerun()
                        
                        with remove_col:
                            if st.button("🗑️", key=f"remove_{row}_{col}", help="Remove court"):
                                # Remove court from this position
                                courts["courts"] = [c for c in courts.get("courts", []) 
                                                  if not (c.get("position", {}).get("row") == row and 
                                                         c.get("position", {}).get("col") == col)]
                                add_audit_log(audit, "Removed Court", f"Court removed from ({row+1}, {col+1})", "admin")
                                st.rerun()
                    
                    # Show edit form if in edit mode
                    if st.session_state.get(f"editing_{row}_{col}", False) or not is_assigned:
                        with st.form(f"court_form_{row}_{col}"):
                            court_name = st.text_input("Court Name", 
                                                     value=current_assignment.get("name", f"Court {assigned_courts + 1}"),
                                                     key=f"name_{position_key}")
                            
                            skill_levels = ["beginner", "intermediate", "advanced"]
                            current_level_idx = skill_levels.index(current_assignment.get("level", "beginner"))
                            skill_level = st.selectbox("Skill Level", skill_levels, 
                                                     index=current_level_idx,
                                                     key=f"level_{position_key}")
                            
                            form_col1, form_col2 = st.columns(2)
                            with form_col1:
                                if st.form_submit_button("💾 Save", use_container_width=True):
                                    if court_name.strip():
                                        # Check if name already exists (except for current court)
                                        existing_names = []
                                        for c in courts.get("courts", []):
                                            if c.get("active", True):
                                                c_pos = c.get("position", {})
                                                if not (c_pos.get("row") == row and c_pos.get("col") == col):
                                                    existing_names.append(c.get("name", ""))
                                        
                                        if court_name in existing_names:
                                            st.error(f"❌ Court name '{court_name}' already exists!")
                                        else:
                                            # Remove existing court at this position
                                            courts["courts"] = [c for c in courts.get("courts", []) 
                                                              if not (c.get("position", {}).get("row") == row and 
                                                                     c.get("position", {}).get("col") == col)]
                                            
                                            # Add/update court
                                            new_id = current_assignment.get("id") or max([c.get("id", 0) for c in courts.get("courts", [])], default=0) + 1
                                            courts["courts"].append({
                                                "id": new_id,
                                                "name": court_name,
                                                "level": skill_level,
                                                "position": {"row": row, "col": col},
                                                "active": True
                                            })
                                            
                                            action = "Updated" if is_assigned else "Added"
                                            add_audit_log(audit, f"{action} Court", f"{court_name} ({skill_level}) at ({row+1}, {col+1})", "admin")
                                            
                                            # Clear edit mode
                                            if f"editing_{row}_{col}" in st.session_state:
                                                del st.session_state[f"editing_{row}_{col}"]
                                            
                                            st.rerun()
                                    else:
                                        st.error("❌ Please enter a court name!")
                            
                            with form_col2:
                                if st.form_submit_button("❌ Cancel", use_container_width=True):
                                    if f"editing_{row}_{col}" in st.session_state:
                                        del st.session_state[f"editing_{row}_{col}"]
                                    st.rerun()
                
                st.markdown("---")
    
    # Summary
    st.markdown("---")
    st.markdown("### 📈 Configuration Summary")
    
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.metric("🎯 Target Courts", total_courts)
    
    with summary_col2:
        st.metric("✅ Assigned Courts", assigned_courts)
    
    with summary_col3:
        remaining = total_courts - assigned_courts
        st.metric("⏳ Remaining", remaining, delta=None if remaining == 0 else f"{remaining} to go")
    
    with summary_col4:
        completion = (assigned_courts / total_courts * 100) if total_courts > 0 else 0
        st.metric("📊 Completion", f"{completion:.0f}%")
    
    # Generate preview
    st.markdown("---")
    st.markdown("### 🖼️ Layout Preview")
    try:
        settings = courts.get("layout_settings", {})
        court_list = courts.get("courts", [])
        
        preview_img = generate_court_image(court_list, settings)
        st.image(preview_img, caption="Court Layout Preview", use_container_width=True)
        
        # Download button
        img_buffer = io.BytesIO()
        preview_img.save(img_buffer, format='PNG')
        st.download_button("📥 Download Layout Image", data=img_buffer.getvalue(),
                          file_name=f"court_layout_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png", 
                          mime="image/png", use_container_width=True)
    except Exception as e:
        st.error(f"Error generating preview: {str(e)}")
    
    # Quick actions
    if assigned_courts > 0:
        st.markdown("---")
        st.markdown("### ⚡ Quick Actions")
        
        quick_col1, quick_col2, quick_col3 = st.columns(3)
        
        with quick_col1:
            if st.button("🎲 Auto-Fill Empty Positions", use_container_width=True):
                # Auto-fill remaining positions
                filled = 0
                for row in range(rows):
                    for col in range(cols):
                        if (row, col) not in court_assignments and assigned_courts + filled < total_courts:
                            filled += 1
                            new_id = max([c.get("id", 0) for c in courts.get("courts", [])], default=0) + 1
                            courts["courts"].append({
                                "id": new_id,
                                "name": f"Court {assigned_courts + filled}",
                                "level": ["beginner", "intermediate", "advanced"][filled % 3],
                                "position": {"row": row, "col": col},
                                "active": True
                            })
                
                if filled > 0:
                    add_audit_log(audit, "Auto-filled Courts", f"{filled} courts auto-generated", "admin")
                    st.success(f"✅ Auto-filled {filled} courts!")
                    st.rerun()
                else:
                    st.info("ℹ️ No empty positions to fill!")
        
        with quick_col2:
            if st.button("📋 Export Configuration", use_container_width=True):
                config_data = {
                    "center_name": center_name,
                    "grid": {"rows": rows, "cols": cols},
                    "courts": courts.get("courts", [])
                }
                st.download_button("📄 Download JSON", 
                                 data=json.dumps(config_data, indent=2),
                                 file_name=f"court_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                 mime="application/json")
        
        with quick_col3:
            if st.button("✅ Finalize Layout", use_container_width=True):
                if assigned_courts == total_courts:
                    st.success("🎉 Layout is complete and ready!")
                    add_audit_log(audit, "Layout Finalized", f"{total_courts} courts configured", "admin")
                else:
                    st.warning(f"⚠️ {total_courts - assigned_courts} courts still need to be assigned!")
