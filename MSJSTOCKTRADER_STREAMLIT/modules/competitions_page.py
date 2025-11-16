import streamlit as st
import pandas as pd
from datetime import datetime
from modules.friends_manager import FriendsManager

def show_comprehensive_leaderboard(user_info, team_manager, badge_system, portfolio_manager, trading_engine):
    """Display comprehensive leaderboard with solo and team competitions."""
    st.title("🏆 Competitions & Leaderboards")
    
    friends_manager = FriendsManager()
    
    # Create tabs for different competition types
    tab1, tab2, tab3, tab4 = st.tabs(["👤 Solo Leaderboard", "🤝 Team Competitions", "🎯 Active Competitions", "🏅 Badge Gallery"])
    
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
            st.info("Add some friends to see the solo leaderboard!")
        
        # Award badges based on performance
        try:
            if badge_system:
                badge_system.check_and_award_badges(
                    user_info['username'], 
                    portfolio_manager, 
                    trading_engine
                )
        except Exception as e:
            st.error(f"Badge system error: {str(e)}")
    
    with tab2:
        st.header("🤝 Team Competition System")
        
        # Check if user is in a team
        user_team = team_manager.get_user_team(user_info['username'])
        
        if user_team:
            st.success(f"You're a member of team: **{user_team['name']}**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Your Team")
                st.write(f"**Team Name:** {user_team['name']}")
                st.write(f"**Captain:** {user_team['captain']}")
                st.write(f"**Members:** {len(user_team['members'])}/10")
                st.write(f"**Total Value:** ${user_team['total_value']:,.2f}")
                st.write(f"**Competitions Won:** {user_team.get('competitions_won', 0)}")
                
                # Show team badges
                team_badges = user_team.get('badges', [])
                if team_badges:
                    st.write("**Team Badges:**")
                    badge_definitions = badge_system.get_badge_definitions()
                    for badge_id in team_badges:
                        if badge_id in badge_definitions:
                            badge = badge_definitions[badge_id]
                            st.write(f"{badge['icon']} {badge['name']}")
                
                # Team member actions
                if user_team['captain'] == user_info['username']:
                    st.write("**🛡️ Captain Controls**")
                    if st.button("Manage Team", key="manage_team"):
                        st.info("Team management features coming soon!")
                
                if st.button("Leave Team", key="leave_team"):
                    result = team_manager.leave_team(user_team['team_id'], user_info['username'])
                    if result['success']:
                        st.success(result['message'])
                        st.rerun()
                    else:
                        st.error(result['message'])
            
            with col2:
                st.subheader("Team Members")
                for member in user_team['members']:
                    member_badge = badge_system.get_badge_display(member)
                    captain_icon = " 👑" if member == user_team['captain'] else ""
                    st.write(f"{member_badge} {member}{captain_icon}")
        else:
            st.info("You're not part of a team yet!")
            
            # Team creation and joining
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Create New Team")
                
                with st.form("create_team_form"):
                    team_name = st.text_input("Team Name")
                    team_description = st.text_area("Team Description (optional)")
                    
                    if st.form_submit_button("Create Team"):
                        if team_name:
                            result = team_manager.create_team(team_name, user_info['username'], team_description)
                            if result['success']:
                                st.success(result['message'])
                                # Award team leader badge
                                badge_system.award_badge(user_info['username'], 'team_leader')
                                st.rerun()
                            else:
                                st.error(result['message'])
                        else:
                            st.error("Please enter a team name")
            
            with col2:
                st.subheader("Join Existing Team")
                
                # Show available teams
                all_teams = team_manager.get_all_teams()
                available_teams = [team for team in all_teams if len(team['members']) < 10]
                
                if available_teams:
                    for team in available_teams[:5]:  # Show top 5 teams
                        with st.container():
                            st.write(f"**{team['name']}**")
                            st.write(f"Members: {len(team['members'])}/10")
                            st.write(f"Total Value: ${team['total_value']:,.2f}")
                            
                            if st.button(f"Join {team['name']}", key=f"join_{team['team_id']}"):
                                result = team_manager.join_team(team['team_id'], user_info['username'])
                                if result['success']:
                                    st.success(result['message'])
                                    # Award team player badge
                                    badge_system.award_badge(user_info['username'], 'team_player')
                                    st.rerun()
                                else:
                                    st.error(result['message'])
                            st.markdown("---")
                else:
                    st.info("No teams available to join. Create your own!")
        
        # Team leaderboard
        st.subheader("🏆 Team Leaderboard")
        team_leaderboard = team_manager.get_team_leaderboard(portfolio_manager)
        
        if team_leaderboard:
            for i, team in enumerate(team_leaderboard[:10]):  # Top 10 teams
                rank = i + 1
                medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")
                
                # Highlight user's team
                is_user_team = user_team and team['team_id'] == user_team['team_id']
                bg_color = "linear-gradient(90deg, #ff6b6b, #ffd93d)" if is_user_team else "#f8f9fa"
                text_color = "white" if is_user_team else "black"
                
                st.markdown(f"""
                <div style="background: {bg_color}; padding: 15px; border-radius: 10px; margin: 10px 0; color: {text_color};">
                    <h4>{medal} {team['name']} {"(Your Team!)" if is_user_team else ""}</h4>
                    <div style="display: flex; justify-content: space-between;">
                        <span><strong>Members:</strong> {team['member_count']}</span>
                        <span><strong>Total Value:</strong> ${team['total_value']:,.2f}</span>
                        <span><strong>Competitions Won:</strong> {team['competitions_won']}</span>
                    </div>
                    <div style="margin-top: 10px;">
                        <strong>Captain:</strong> {team['captain']} | 
                        <strong>Members:</strong> {', '.join(team['members'][:3])}{"..." if len(team['members']) > 3 else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No teams found!")
    
    with tab3:
        st.header("🎯 Active Competitions")
        
        # Get active competitions
        active_competitions = team_manager.get_active_competitions()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏃 Solo Competitions")
            
            if active_competitions['solo']:
                for comp in active_competitions['solo']:
                    with st.container():
                        st.write(f"**{comp['name']}**")
                        
                        end_date = datetime.fromisoformat(comp['end_date'])
                        time_left = end_date - datetime.now()
                        
                        if time_left.total_seconds() > 0:
                            days = time_left.days
                            hours = time_left.seconds // 3600
                            st.write(f"⏰ {days}d {hours}h remaining")
                        else:
                            st.write("⏰ Ended")
                        
                        st.write(f"Participants: {len(comp['participants'])}")
                        
                        # Show prizes
                        if comp['prizes']:
                            st.write("**Prizes:**")
                            for prize in comp['prizes']:
                                badge_def = badge_system.get_badge_definitions().get(prize['badge'], {})
                                icon = badge_def.get('icon', '🏆')
                                st.write(f"{prize['position']}. {icon} {prize['name']}")
                        
                        st.markdown("---")
            else:
                st.info("No active solo competitions")
                
                # Create new solo competition (admin only)
                if user_info.get('role') in ['admin', 'super_admin']:
                    if st.button("Start Solo Competition"):
                        result = team_manager.start_competition("solo", "Weekly Solo Challenge", 7)
                        if result['success']:
                            st.success("Solo competition started!")
                            st.rerun()
        
        with col2:
            st.subheader("👥 Team Competitions")
            
            if active_competitions['team']:
                for comp in active_competitions['team']:
                    with st.container():
                        st.write(f"**{comp['name']}**")
                        
                        end_date = datetime.fromisoformat(comp['end_date'])
                        time_left = end_date - datetime.now()
                        
                        if time_left.total_seconds() > 0:
                            days = time_left.days
                            hours = time_left.seconds // 3600
                            st.write(f"⏰ {days}d {hours}h remaining")
                        else:
                            st.write("⏰ Ended")
                        
                        st.write(f"Teams: {len(comp['participants'])}")
                        
                        # Show prizes
                        if comp['prizes']:
                            st.write("**Prizes:**")
                            for prize in comp['prizes']:
                                badge_def = badge_system.get_badge_definitions().get(prize['badge'], {})
                                icon = badge_def.get('icon', '🏆')
                                st.write(f"{prize['position']}. {icon} {prize['name']}")
                        
                        st.markdown("---")
            else:
                st.info("No active team competitions")
                
                # Create new team competition (admin only)
                if user_info.get('role') in ['admin', 'super_admin']:
                    if st.button("Start Team Competition"):
                        result = team_manager.start_competition("team", "Monthly Team Challenge", 30)
                        if result['success']:
                            st.success("Team competition started!")
                            st.rerun()
    
    with tab4:
        st.header("🏅 Badge Gallery & Achievements")
        
        # Get user badges
        user_badges = badge_system.get_user_badges(user_info['username'])
        badge_definitions = badge_system.get_badge_definitions()
        
        # Badge equipping section
        st.subheader("🎯 Your Badge Collection")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Currently Equipped:**")
            equipped_badge = user_badges.get('equipped_badge', 'newcomer')
            if equipped_badge in badge_definitions:
                badge = badge_definitions[equipped_badge]
                st.markdown(f"""
                <div style="background: linear-gradient(45deg, #667eea, #764ba2); 
                           padding: 20px; border-radius: 10px; text-align: center; color: white;">
                    <h2>{badge['icon']}</h2>
                    <h4>{badge['name']}</h4>
                    <p>{badge['description']}</p>
                    <small>Rarity: {badge['rarity'].title()}</small>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.write("**Change Badge:**")
            owned_badges = user_badges.get('owned_badges', ['newcomer'])
            
            for badge_id in owned_badges:
                if badge_id in badge_definitions:
                    badge = badge_definitions[badge_id]
                    
                    if st.button(f"{badge['icon']} {badge['name']}", key=f"equip_{badge_id}"):
                        if badge_system.equip_badge(user_info['username'], badge_id):
                            st.success(f"Equipped {badge['name']}!")
                            st.rerun()
        
        # Badge gallery by category
        st.subheader("🌟 All Available Badges")
        
        badges_by_category = badge_system.get_badges_by_category()
        
        for category, badges in badges_by_category.items():
            with st.expander(f"{category.title()} Badges ({len(badges)} total)"):
                
                # Create grid layout
                cols = st.columns(3)
                
                for i, badge in enumerate(badges):
                    with cols[i % 3]:
                        badge_id = badge['id']
                        is_owned = badge_id in user_badges.get('owned_badges', [])
                        
                        # Color coding by rarity
                        rarity_colors = {
                            'common': '#28a745',
                            'rare': '#007bff', 
                            'epic': '#6f42c1',
                            'legendary': '#fd7e14'
                        }
                        
                        color = rarity_colors.get(badge['rarity'], '#6c757d')
                        opacity = "1.0" if is_owned else "0.5"
                        
                        st.markdown(f"""
                        <div style="background: {color}; opacity: {opacity}; 
                                   padding: 15px; border-radius: 10px; text-align: center; 
                                   color: white; margin: 10px 0;">
                            <h3>{badge['icon']}</h3>
                            <h5>{badge['name']}</h5>
                            <p style="font-size: 12px;">{badge['description']}</p>
                            <small>{badge['rarity'].title()}</small>
                            {"<br><strong>✅ OWNED</strong>" if is_owned else "<br><em>🔒 Not Owned</em>"}
                        </div>
                        """, unsafe_allow_html=True)