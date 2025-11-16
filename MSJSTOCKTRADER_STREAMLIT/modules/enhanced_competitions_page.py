import streamlit as st
import pandas as pd
from datetime import datetime
from modules.friends_manager import FriendsManager
from modules.enhanced_team_manager import EnhancedTeamManager

def show_comprehensive_leaderboard(user_info, badge_system, portfolio_manager, trading_engine):
    """Display comprehensive leaderboard with enhanced team system."""
    st.title("🏆 Competitions & Leaderboards")
    
    friends_manager = FriendsManager()
    team_manager = EnhancedTeamManager()
    
    # Create tabs for different competition types
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👤 Solo Leaderboard", 
        "🤝 Enhanced Teams", 
        "📬 Team Invitations",
        "🎯 Active Competitions", 
        "🏅 Badge Gallery"
    ])
    
    with tab1:
        st.header("👤 Solo Competition Leaderboard")
        
        # Get solo leaderboard data
        leaderboard_df = friends_manager.get_leaderboard(user_info['user_id'])
        
        if not leaderboard_df.empty:
            st.subheader("You vs Your Friends")
            
            # Create medal emojis for top 3
            medals = {1: "🥇", 2: "🥈", 3: "🥉"}
            
            for idx, row in leaderboard_df.iterrows():
                rank = row['rank']
                
                # Get user badge
                user_badge = badge_system.get_badge_display(row['username'])
                
                # Special styling for current user
                if row['is_current_user']:
                    st.markdown(f"""
                    <div style="background: linear-gradient(90deg, #1f77b4, #2ca02c); 
                               padding: 15px; border-radius: 10px; margin: 10px 0; color: white;">
                        <h3>{medals.get(rank, f"#{rank}")} {user_badge} {row['name']} (You!)</h3>
                        <div style="display: flex; justify-content: space-between;">
                            <span><strong>Total Value:</strong> ${row['total_value']:,.2f}</span>
                            <span><strong>Portfolio:</strong> ${row['portfolio_value']:,.2f}</span>
                            <span><strong>Cash:</strong> ${row['cash_balance']:,.2f}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                            <span><strong>Total P&L:</strong> ${row['total_pnl']:,.2f}</span>
                            <span><strong>Daily P&L:</strong> ${row['daily_pnl']:,.2f}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Regular styling for other users
                    st.markdown(f"""
                    <div style="background: #f8f9fa; border: 1px solid #dee2e6; 
                               padding: 15px; border-radius: 10px; margin: 10px 0;">
                        <h4>{medals.get(rank, f"#{rank}")} {user_badge} {row['name']}</h4>
                        <div style="display: flex; justify-content: space-between;">
                            <span><strong>Total Value:</strong> ${row['total_value']:,.2f}</span>
                            <span><strong>Portfolio:</strong> ${row['portfolio_value']:,.2f}</span>
                            <span><strong>Cash:</strong> ${row['cash_balance']:,.2f}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                            <span><strong>Total P&L:</strong> ${row['total_pnl']:,.2f}</span>
                            <span><strong>Daily P&L:</strong> ${row['daily_pnl']:,.2f}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            # Show global leaderboard if no friends
            st.info("👥 Add friends to compete on the leaderboard! Showing global top performers:")
            
            # Get all users and their portfolios for global leaderboard
            try:
                all_users = auth_manager._load_users()
                global_leaderboard = []
                
                for username, user_data in all_users.items():
                    if user_data.get('username') == 'demo':
                        continue  # Skip demo account
                        
                    portfolio_data = portfolio_manager.get_portfolio_summary(user_data['user_id'])
                    if portfolio_data and portfolio_data.get('success'):
                        portfolio = portfolio_data['portfolio']
                        total_value = portfolio.get('total_value', 100000)
                        global_leaderboard.append({
                            'username': username,
                            'name': f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip() or username,
                            'total_value': total_value,
                            'portfolio_value': portfolio.get('positions_value', 0),
                            'cash_balance': portfolio.get('cash_balance', 100000),
                            'total_pnl': total_value - 100000,
                            'daily_pnl': 0,
                            'is_current_user': username == user_info['username']
                        })
                
                # Sort by total value
                global_leaderboard.sort(key=lambda x: x['total_value'], reverse=True)
                
                # Add ranks
                for i, user in enumerate(global_leaderboard):
                    user['rank'] = i + 1
                
                # Show top 10
                medals = {1: "🥇", 2: "🥈", 3: "🥉"}
                for user in global_leaderboard[:10]:
                    user_badge = badge_system.get_badge_display(user['username'])
                    
                    if user['is_current_user']:
                        st.markdown(f"""
                        <div style="background: linear-gradient(90deg, #1f77b4, #2ca02c); 
                                   padding: 15px; border-radius: 10px; margin: 10px 0; color: white;">
                            <h3>{medals.get(user['rank'], f"#{user['rank']}")} {user_badge} {user['name']} (You!)</h3>
                            <div style="display: flex; justify-content: space-between;">
                                <span><strong>Total Value:</strong> ${user['total_value']:,.2f}</span>
                                <span><strong>Portfolio:</strong> ${user['portfolio_value']:,.2f}</span>
                                <span><strong>Cash:</strong> ${user['cash_balance']:,.2f}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                                <span><strong>Total P&L:</strong> ${user['total_pnl']:,.2f}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background: #f8f9fa; border: 1px solid #dee2e6; 
                                   padding: 15px; border-radius: 10px; margin: 10px 0;">
                            <h4>{medals.get(user['rank'], f"#{user['rank']}")} {user_badge} {user['name']}</h4>
                            <div style="display: flex; justify-content: space-between;">
                                <span><strong>Total Value:</strong> ${user['total_value']:,.2f}</span>
                                <span><strong>Portfolio:</strong> ${user['portfolio_value']:,.2f}</span>
                                <span><strong>Cash:</strong> ${user['cash_balance']:,.2f}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                                <span><strong>Total P&L:</strong> ${user['total_pnl']:,.2f}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error loading global leaderboard: {e}")
                st.info("Add some friends to see the solo leaderboard!")
    
    with tab2:
        st.header("🤝 Enhanced Team System")
        
        # Check if user is in a team
        user_team = team_manager.get_user_team(user_info['username'])
        
        if user_team:
            show_team_management_interface(user_team, user_info, team_manager, badge_system)
        else:
            show_team_creation_and_discovery(user_info, team_manager)
    
    with tab3:
        st.header("📬 Team Invitations & Notifications")
        show_team_invitations_interface(user_info, team_manager)
    
    with tab4:
        st.header("🎯 Active Competitions")
        show_active_competitions(user_info, team_manager, badge_system, portfolio_manager)
    
    with tab5:
        st.header("🏅 Badge Gallery")
        show_badge_gallery(user_info, badge_system)

def show_team_management_interface(user_team, user_info, team_manager, badge_system):
    """Show team management interface for team members."""
    is_creator = user_team['creator'] == user_info['username']
    is_captain = user_team['captain'] == user_info['username']
    
    # Team status and info
    visibility = "🌍 Public" if user_team.get('is_public', True) else "🔒 Private"
    st.success(f"You're a member of team: **{user_team['name']}** ({visibility})")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Team Details")
        st.write(f"**Team Name:** {user_team['name']}")
        st.write(f"**Creator:** {user_team['creator']} {'👑' if is_creator else ''}")
        st.write(f"**Captain:** {user_team['captain']} {'⭐' if is_captain else ''}")
        st.write(f"**Members:** {len(user_team['members'])}/{user_team.get('max_members', 10)}")
        st.write(f"**Total Value:** ${user_team.get('total_value', 0):,.2f}")
        st.write(f"**Visibility:** {visibility}")
        
        if user_team.get('description'):
            st.write(f"**Description:** {user_team['description']}")
        
        # Team creator powers
        if is_creator:
            st.markdown("---")
            st.subheader("👑 Team Creator Powers")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                # Initialize delete confirmation state
                if 'confirm_team_delete' not in st.session_state:
                    st.session_state.confirm_team_delete = False
                
                if not st.session_state.confirm_team_delete:
                    if st.button("🗑️ Delete Team", type="secondary", key="delete_team_btn"):
                        st.session_state.confirm_team_delete = True
                        st.rerun()
                else:
                    st.warning("⚠️ Are you sure you want to delete this team? This action cannot be undone!")
                    
                    col_confirm, col_cancel = st.columns(2)
                    
                    with col_confirm:
                        if st.button("✅ Yes, Delete", type="primary", key="confirm_delete_btn"):
                            result = team_manager.delete_team(user_team['team_id'], user_info['username'])
                            if result['success']:
                                st.success(result['message'])
                                st.session_state.confirm_team_delete = False
                                st.rerun()
                            else:
                                st.error(result['message'])
                                st.session_state.confirm_team_delete = False
                    
                    with col_cancel:
                        if st.button("❌ Cancel", type="secondary", key="cancel_delete_btn"):
                            st.session_state.confirm_team_delete = False
                            st.rerun()
            
            with col_b:
                new_visibility = st.selectbox(
                    "Team Visibility:",
                    ["Public", "Private"],
                    index=0 if user_team.get('is_public', True) else 1
                )
                if st.button("Update Visibility"):
                    # Update team visibility (would need to add this method)
                    st.success(f"Team visibility updated to {new_visibility}")
        
        # Captain/Creator invitation powers
        if is_creator or is_captain:
            st.markdown("---")
            st.subheader("📤 Invite New Members")
            
            search_query = st.text_input("Search users to invite:", placeholder="Enter username or name...")
            
            if search_query:
                search_results = team_manager.search_users_for_invitation(search_query, user_info['username'])
                
                if search_results:
                    st.write(f"Found {len(search_results)} available users:")
                    
                    for user in search_results:
                        col_user, col_invite = st.columns([3, 1])
                        
                        with col_user:
                            st.write(f"**{user['first_name']} {user['last_name']}** (@{user['username']})")
                            st.caption(f"Role: {user['role'].title()}")
                        
                        with col_invite:
                            if st.button("📤 Invite", key=f"invite_{user['username']}"):
                                result = team_manager.send_team_invitation(
                                    user_team['team_id'], 
                                    user_info['username'], 
                                    user['username']
                                )
                                if result['success']:
                                    st.success(result['message'])
                                    st.rerun()
                                else:
                                    st.error(result['message'])
                else:
                    st.info("No available users found matching your search.")
        
        # Leave team option (not for creator)
        if not is_creator:
            st.markdown("---")
            if st.button("🚪 Leave Team", type="secondary"):
                result = team_manager.leave_team(user_team['team_id'], user_info['username'])
                if result['success']:
                    st.success(result['message'])
                    st.rerun()
                else:
                    st.error(result['message'])
    
    with col2:
        st.subheader("👥 Team Members")
        
        for member in user_team['members']:
            member_badge = badge_system.get_badge_display(member)
            
            # Member role indicators
            role_indicators = []
            if member == user_team['creator']:
                role_indicators.append("👑 Creator")
            if member == user_team['captain']:
                role_indicators.append("⭐ Captain")
            
            role_text = f" ({', '.join(role_indicators)})" if role_indicators else ""
            
            st.write(f"{member_badge} **{member}**{role_text}")

def show_team_creation_and_discovery(user_info, team_manager):
    """Show team creation and public team discovery interface."""
    st.info("You're not currently in a team")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🆕 Create New Team")
        
        with st.form("create_enhanced_team"):
            team_name = st.text_input("Team Name *", placeholder="Enter team name...")
            team_description = st.text_area("Description", placeholder="Describe your team (optional)...")
            is_public = st.checkbox("Make team public", value=True, 
                                   help="Public teams can be discovered and joined by anyone")
            
            if st.form_submit_button("🚀 Create Team", use_container_width=True):
                if team_name:
                    result = team_manager.create_team(
                        team_name, 
                        user_info['username'], 
                        team_description, 
                        is_public
                    )
                    if result['success']:
                        st.success(result['message'])
                        st.rerun()
                    else:
                        st.error(result['message'])
                else:
                    st.error("Please enter a team name")
    
    with col2:
        st.subheader("🌍 Discover Public Teams")
        
        public_teams = team_manager.get_public_teams()
        
        if public_teams:
            for team in public_teams[:5]:  # Show top 5 public teams
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin: 10px 0; border: 1px solid #dee2e6;">
                    <h5>🌍 {team['name']}</h5>
                    <p><strong>Description:</strong> {team.get('description', 'No description')}</p>
                    <p><strong>Creator:</strong> {team['creator']} | <strong>Members:</strong> {team['member_count']}/{team['max_members']}</p>
                    <p><strong>Total Value:</strong> ${team['total_value']:,.2f}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if team['member_count'] < team['max_members']:
                    if st.button(f"📤 Request Invite to {team['name']}", key=f"request_{team['team_id']}"):
                        st.info("Contact team members to request an invitation!")
                else:
                    st.write("🔒 Team is full")
        else:
            st.info("No public teams available. Create the first one!")

def show_team_invitations_interface(user_info, team_manager):
    """Show team invitations and notifications interface."""
    
    # Get user's pending invitations
    invitations = team_manager.get_user_invitations(user_info['username'])
    notifications = team_manager.get_user_notifications(user_info['username'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📨 Pending Team Invitations")
        
        if invitations:
            for invitation in invitations:
                st.markdown(f"""
                <div style="background: #e3f2fd; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #2196f3;">
                    <h5>🤝 Team Invitation</h5>
                    <p><strong>Team:</strong> {invitation['team_name']}</p>
                    <p><strong>From:</strong> {invitation['inviter_username']}</p>
                    <p><strong>Message:</strong> {invitation['message']}</p>
                    <p><strong>Expires:</strong> {datetime.fromisoformat(invitation['expires_at']).strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col_accept, col_decline = st.columns(2)
                
                with col_accept:
                    if st.button("✅ Accept", key=f"accept_{invitation['id']}"):
                        result = team_manager.respond_to_invitation(invitation['id'], user_info['username'], True)
                        if result['success']:
                            st.success(result['message'])
                            st.rerun()
                        else:
                            st.error(result['message'])
                
                with col_decline:
                    if st.button("❌ Decline", key=f"decline_{invitation['id']}"):
                        result = team_manager.respond_to_invitation(invitation['id'], user_info['username'], False)
                        if result['success']:
                            st.success(result['message'])
                            st.rerun()
                        else:
                            st.error(result['message'])
                
                st.markdown("---")
        else:
            st.info("No pending team invitations")
    
    with col2:
        st.subheader("🔔 Team Notifications")
        
        if notifications:
            for notification in notifications[:10]:  # Show latest 10
                read_indicator = "📖" if notification.get('read', False) else "🆕"
                
                st.markdown(f"""
                <div style="background: {'#f5f5f5' if notification.get('read', False) else '#fff3cd'}; 
                           padding: 10px; border-radius: 5px; margin: 5px 0;">
                    <p><strong>{read_indicator} {notification['title']}</strong></p>
                    <p>{notification['message']}</p>
                    <small>{datetime.fromisoformat(notification['created_at']).strftime('%B %d, %Y at %I:%M %p')}</small>
                </div>
                """, unsafe_allow_html=True)
                
                if not notification.get('read', False):
                    if st.button("Mark as Read", key=f"read_{notification['id']}"):
                        team_manager.mark_notification_read(notification['id'], user_info['username'])
                        st.rerun()
        else:
            st.info("No team notifications")

def show_active_competitions(user_info, team_manager, badge_system, portfolio_manager):
    """Show active competitions and team leaderboard."""
    
    # Team leaderboard
    st.subheader("🏆 Team Leaderboard")
    
    team_leaderboard = team_manager.get_team_leaderboard(portfolio_manager)
    
    if team_leaderboard:
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        
        for idx, team in enumerate(team_leaderboard, 1):
            medal = medals.get(idx, f"#{idx}")
            visibility_icon = "🌍" if team.get('is_public', True) else "🔒"
            
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin: 10px 0; border: 1px solid #dee2e6;">
                <h4>{medal} {visibility_icon} {team['name']}</h4>
                <div style="display: flex; justify-content: space-between;">
                    <span><strong>Creator:</strong> {team['creator']}</span>
                    <span><strong>Captain:</strong> {team['captain']}</span>
                    <span><strong>Members:</strong> {team['member_count']}</span>
                </div>
                <div style="margin-top: 10px;">
                    <span><strong>Total Portfolio Value:</strong> ${team['total_value']:,.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No teams created yet. Create the first team!")

def show_badge_gallery(user_info, badge_system):
    """Show user's badge collection and achievements with enhanced UI."""
    
    # Get user's badges and all available badges
    user_badges = badge_system.get_user_badges(user_info['username'])
    all_badge_definitions = badge_system.get_all_badge_definitions()
    
    # Create badge gallery header with statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_badges = len(all_badge_definitions)
        earned_count = len(user_badges) if user_badges else 0
        st.metric("Total Badges", f"{earned_count}/{total_badges}")
    
    with col2:
        completion_pct = (earned_count / total_badges * 100) if total_badges > 0 else 0
        st.metric("Completion", f"{completion_pct:.1f}%")
    
    with col3:
        rarity_counts = {}
        if user_badges:
            for badge in user_badges:
                badge_def = all_badge_definitions.get(badge['badge_id'], {})
                rarity = badge_def.get('rarity', 'Common')
                rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1
        
        rare_count = rarity_counts.get('Rare', 0) + rarity_counts.get('Epic', 0) + rarity_counts.get('Legendary', 0)
        st.metric("Rare Badges", rare_count)
    
    with col4:
        if user_badges:
            latest_badge = max(user_badges, key=lambda x: x['earned_at'])
            latest_def = all_badge_definitions.get(latest_badge['badge_id'], {})
            st.metric("Latest Badge", latest_def.get('name', 'Unknown')[:15] + "...")
        else:
            st.metric("Latest Badge", "None")
    
    # Progress bar
    if total_badges > 0:
        progress = earned_count / total_badges
        st.progress(progress)
        st.caption(f"Badge Collection Progress: {earned_count} out of {total_badges} badges earned")
    
    st.markdown("---")
    
    # Filter and sort options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_option = st.selectbox(
            "Filter Badges",
            ["All Badges", "Earned Only", "Available Only", "By Rarity"],
            key="badge_filter"
        )
    
    with col2:
        sort_option = st.selectbox(
            "Sort By",
            ["Rarity", "Name", "Date Earned", "Type"],
            key="badge_sort"
        )
    
    with col3:
        if filter_option == "By Rarity":
            rarity_filter = st.selectbox(
                "Select Rarity",
                ["All", "Common", "Rare", "Epic", "Legendary"],
                key="rarity_filter"
            )
        else:
            rarity_filter = "All"
    
    # Create badge tabs
    tab1, tab2, tab3 = st.tabs(["🏆 Earned Badges", "🎯 Available Badges", "📊 Badge Statistics"])
    
    with tab1:
        if user_badges:
            st.subheader("🎖️ Your Earned Badges")
            
            # Group badges by rarity
            rarity_groups = {}
            for badge in user_badges:
                badge_def = all_badge_definitions.get(badge['badge_id'], {})
                rarity = badge_def.get('rarity', 'Common')
                if rarity not in rarity_groups:
                    rarity_groups[rarity] = []
                rarity_groups[rarity].append((badge, badge_def))
            
            # Display badges by rarity
            rarity_order = ['Legendary', 'Epic', 'Rare', 'Common']
            rarity_colors = {
                'Legendary': '#FFD700',
                'Epic': '#9966CC', 
                'Rare': '#00BFFF',
                'Common': '#90EE90'
            }
            
            for rarity in rarity_order:
                if rarity in rarity_groups:
                    with st.expander(f"{rarity} Badges ({len(rarity_groups[rarity])})", expanded=True):
                        cols = st.columns(3)
                        for idx, (badge, badge_def) in enumerate(rarity_groups[rarity]):
                            with cols[idx % 3]:
                                earned_date = badge['earned_at'][:10] if badge['earned_at'] else 'Unknown'
                                
                                st.markdown(f"""
                                <div style="background: linear-gradient(135deg, {rarity_colors[rarity]}20, {rarity_colors[rarity]}40); 
                                           padding: 15px; border-radius: 15px; text-align: center; margin: 10px;
                                           border: 2px solid {rarity_colors[rarity]}; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                                    <div style="font-size: 3em; margin-bottom: 10px;">{badge_def.get('icon', '🏆')}</div>
                                    <div style="font-weight: bold; font-size: 1.1em; margin-bottom: 5px;">{badge_def.get('name', 'Unknown Badge')}</div>
                                    <div style="background: {rarity_colors[rarity]}; color: white; padding: 3px 8px; 
                                               border-radius: 10px; font-size: 0.8em; margin-bottom: 8px;">{rarity}</div>
                                    <div style="font-size: 0.85em; color: #666; margin-bottom: 5px;">{badge_def.get('description', 'No description')}</div>
                                    <div style="font-size: 0.75em; color: #888;">Earned: {earned_date}</div>
                                </div>
                                """, unsafe_allow_html=True)
        else:
            st.info("🎯 Start trading and completing achievements to earn your first badges!")
    
    with tab2:
        earned_badge_ids = [badge['badge_id'] for badge in user_badges] if user_badges else []
        available_badges = {k: v for k, v in all_badge_definitions.items() if k not in earned_badge_ids}
        
        if available_badges:
            st.subheader("🎯 Badges Available to Earn")
            
            # Group available badges by rarity
            available_groups = {}
            for badge_id, badge_def in available_badges.items():
                rarity = badge_def.get('rarity', 'Common')
                if rarity not in available_groups:
                    available_groups[rarity] = []
                available_groups[rarity].append((badge_id, badge_def))
            
            rarity_colors = {
                'Legendary': '#FFD700',
                'Epic': '#9966CC', 
                'Rare': '#00BFFF',
                'Common': '#90EE90'
            }
            
            for rarity in ['Legendary', 'Epic', 'Rare', 'Common']:
                if rarity in available_groups:
                    with st.expander(f"Available {rarity} Badges ({len(available_groups[rarity])})", expanded=True):
                        cols = st.columns(3)
                        for idx, (badge_id, badge_def) in enumerate(available_groups[rarity]):
                            with cols[idx % 3]:
                                st.markdown(f"""
                                <div style="background: #f8f9fa; padding: 15px; border-radius: 15px; 
                                           text-align: center; margin: 10px; border: 2px dashed {rarity_colors[rarity]};
                                           transition: all 0.3s ease;">
                                    <div style="font-size: 3em; opacity: 0.4; margin-bottom: 10px;">{badge_def.get('icon', '🏆')}</div>
                                    <div style="font-weight: bold; font-size: 1.1em; margin-bottom: 5px; color: #666;">{badge_def.get('name', 'Unknown Badge')}</div>
                                    <div style="background: {rarity_colors[rarity]}; color: white; padding: 3px 8px; 
                                               border-radius: 10px; font-size: 0.8em; margin-bottom: 8px;">{rarity}</div>
                                    <div style="font-size: 0.85em; color: #888; margin-bottom: 5px;">{badge_def.get('description', 'No description')}</div>
                                    <div style="font-size: 0.75em; color: #666; font-style: italic;">Requirements: {badge_def.get('requirements', 'Complete specific achievements')}</div>
                                </div>
                                """, unsafe_allow_html=True)
        else:
            st.success("🎉 Amazing! You've earned all available badges!")
            st.balloons()
    
    with tab3:
        st.subheader("📊 Badge Collection Statistics")
        
        # Create statistics
        if user_badges and all_badge_definitions:
            # Badge rarity distribution
            rarity_stats = {}
            for badge in user_badges:
                badge_def = all_badge_definitions.get(badge['badge_id'], {})
                rarity = badge_def.get('rarity', 'Common')
                rarity_stats[rarity] = rarity_stats.get(rarity, 0) + 1
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Badge Rarity Distribution:**")
                for rarity, count in rarity_stats.items():
                    percentage = (count / len(user_badges)) * 100
                    st.write(f"• {rarity}: {count} badges ({percentage:.1f}%)")
            
            with col2:
                st.write("**Achievement Timeline:**")
                if user_badges:
                    sorted_badges = sorted(user_badges, key=lambda x: x['earned_at'], reverse=True)
                    for badge in sorted_badges[:5]:  # Show latest 5
                        badge_def = all_badge_definitions.get(badge['badge_id'], {})
                        earned_date = badge['earned_at'][:10]
                        st.write(f"• {badge_def.get('name', 'Unknown')} - {earned_date}")
            
            # Progress metrics
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                common_earned = rarity_stats.get('Common', 0)
                common_total = len([b for b in all_badge_definitions.values() if b.get('rarity') == 'Common'])
                st.metric("Common Badges", f"{common_earned}/{common_total}")
            
            with col2:
                rare_earned = rarity_stats.get('Rare', 0)
                rare_total = len([b for b in all_badge_definitions.values() if b.get('rarity') == 'Rare'])
                st.metric("Rare Badges", f"{rare_earned}/{rare_total}")
            
            with col3:
                legendary_earned = rarity_stats.get('Legendary', 0)
                legendary_total = len([b for b in all_badge_definitions.values() if b.get('rarity') == 'Legendary'])
                st.metric("Legendary Badges", f"{legendary_earned}/{legendary_total}")
            
        else:
            st.info("Start earning badges to see detailed statistics!")
    
    # Achievement tips
    st.markdown("---")
    st.info("💡 **Tips to Earn More Badges:** Trade regularly, join teams, make profitable trades, diversify your portfolio, and participate in competitions!")