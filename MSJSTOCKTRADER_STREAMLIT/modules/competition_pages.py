import streamlit as st
from datetime import datetime, timedelta
from modules.competition_manager import CompetitionManager
from modules.data_cleanup_manager import DataCleanupManager
from modules.portfolio_manager import PortfolioManager

def show_competition_status_page():
    """Display current competition status and leaderboard."""
    st.title("🏆 Trading Competition")
    
    competition_manager = CompetitionManager()
    portfolio_manager = PortfolioManager()
    
    # Get current season (always reload fresh data from file)
    current_season = competition_manager.get_current_season()
    
    if not current_season:
        st.warning("⚠️ No active competition season. Check back later!")
        
        # Show past winners
        show_past_winners()
        
        st.divider()
        
        # Allow data export even without active season
        st.info("📥 You can still download your trading history anytime!")
        
        if st.button("📥 Download My Trading Data", type="secondary"):
            show_data_export_dialog()
        
        return
    
    # Reload fresh participant list from current season
    current_season = competition_manager.get_current_season()  # Reload to ensure we have latest data
    
    # Competition info
    st.success(f"**Season {current_season['season_number']} is Active!**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_date = datetime.fromisoformat(current_season['start_date'])
        st.metric("Started", start_date.strftime("%B %d, %Y"))
    
    with col2:
        end_date = datetime.fromisoformat(current_season['end_date'])
        st.metric("Ends", end_date.strftime("%B %d, %Y"))
    
    with col3:
        days_left = (end_date - datetime.now()).days
        st.metric("Days Remaining", days_left)
    
    # Progress bar
    total_days = (end_date - start_date).days
    days_passed = (datetime.now() - start_date).days
    progress = min(days_passed / total_days, 1.0)
    
    st.progress(progress)
    st.caption(f"Competition is {progress*100:.1f}% complete")
    
    st.divider()
    
    # Registration button
    user_id = st.session_state.user_info['user_id']
    username = st.session_state.user_info['username']
    
    participants = current_season.get('participants', [])
    is_registered = any(p['user_id'] == user_id for p in participants)
    
    if is_registered:
        st.info(f"✅ You're registered for Season {current_season['season_number']}!")
    else:
        if st.button("🎯 Join Competition", type="primary"):
            result = competition_manager.add_participant(user_id, username)
            if result['success']:
                st.success(result['message'])
                st.rerun()
            else:
                st.error(result['message'])
    
    st.divider()
    
    # Global Leaderboard - Show ALL users ranked by total portfolio value
    st.subheader("📊 Global Leaderboard - All Investors")
    st.caption(f"📈 Showing all traders ranked by total portfolio value (started with $100,000)")
    
    # Load all users
    import json
    try:
        with open('data/users.json', 'r') as f:
            all_users = json.load(f)
    except:
        all_users = {}
    
    if not all_users:
        st.info("No traders registered yet!")
    else:
        # Calculate rankings for ALL users
        rankings = []
        for user_id_key, user_data in all_users.items():
            try:
                user_portfolio = portfolio_manager.get_portfolio_summary(user_id_key)
                if user_portfolio['success']:
                    total_value = user_portfolio['portfolio']['total_value']
                    profit = total_value - 100000  # Calculate profit from starting amount
                    
                    # Get the actual user_id from user data (not the dict key)
                    actual_user_id = user_data.get('user_id', user_id_key)
                    
                    rankings.append({
                        'username': user_data.get('username', 'Unknown'),
                        'total_value': total_value,
                        'profit': profit,
                        'user_id': user_id_key,  # Keep using dict key for current user comparison
                        'is_participant': any(p['user_id'] == actual_user_id for p in participants)  # Use actual UUID for participant check
                    })
            except:
                continue
        
        # Sort by total value
        rankings.sort(key=lambda x: x['total_value'], reverse=True)
        
        # Display top rankings
        display_limit = st.selectbox("Show top:", [10, 25, 50, 100, "All"], index=0)
        if display_limit == "All":
            display_limit = len(rankings)
        
        for i, rank in enumerate(rankings[:display_limit], 1):
            is_current_user = rank['user_id'] == user_id
            
            medal = ""
            if i == 1:
                medal = "🥇"
            elif i == 2:
                medal = "🥈"
            elif i == 3:
                medal = "🥉"
            
            # Color based on profit/loss
            profit_color = "#2e7d32" if rank['profit'] >= 0 else "#c62828"
            profit_symbol = "+" if rank['profit'] >= 0 else ""
            
            # Highlight current user
            if is_current_user:
                bg_color = "#e3f2fd"
                border_style = "2px solid #1976d2"
            else:
                bg_color = "#fafafa"
                border_style = "1px solid #e0e0e0"
            
            # Show if participant in current season
            participant_badge = " 🎯" if rank['is_participant'] else ""
            
            st.markdown(f"""
            <div style="background-color: {bg_color}; padding: 12px; border-radius: 8px; margin: 5px 0; border: {border_style};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{medal} #{i}</strong> - {rank['username']}{participant_badge}
                        {" <span style='color: #1976d2; font-weight: bold;'>(You)</span>" if is_current_user else ""}
                    </div>
                    <div style="text-align: right;">
                        <div><strong style="font-size: 16px;">${rank['total_value']:,.2f}</strong></div>
                        <div style="color: {profit_color}; font-size: 14px;">{profit_symbol}${rank['profit']:,.2f}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if len(rankings) > display_limit:
            st.info(f"Showing top {display_limit} of {len(rankings)} traders")
    
    st.divider()
    
    # Data deletion warning
    st.warning("""
    **⚠️ Important: Data Cleanup Policy**
    
    At the end of each 6-month competition season:
    - All trading data older than 6 months will be **permanently deleted**
    - Your **user account will NOT be deleted**
    - All positions will be **liquidated**
    - Your portfolio will be **reset to $100,000**
    
    **You will receive notifications:**
    - 30 days before deletion
    - 7 days before deletion  
    - 1 day before deletion
    
    **Make sure to download your data before it's deleted!**
    """)
    
    if st.button("📥 Download My Trading Data", type="secondary"):
        show_data_export_dialog()

def show_data_export_dialog():
    """Show data export options."""
    st.subheader("📥 Export Your Trading Data")
    
    cleanup_manager = DataCleanupManager()
    user_id = st.session_state.user_info['user_id']
    
    format_choice = st.radio("Select Export Format:", ["CSV", "JSON"])
    
    if st.button("Generate Export"):
        with st.spinner("Preparing your data..."):
            result = cleanup_manager.export_user_data(user_id, format_choice.lower())
            
            if result['success']:
                # Show summary
                if format_choice == "CSV" and 'summary' in result:
                    summary = result['summary']
                    st.info(f"""
                    **Export Summary**
                    - User ID: {summary['user_id']}
                    - Export Date: {summary['export_date']}
                    - Cash Balance: ${summary['cash_balance']:,.2f}
                    - Total Trades: {summary['total_trades']}
                    - Active Positions: {summary['active_positions']}
                    """)
                
                st.success(f"✅ Export ready! ({result['total_trades']} trades)")
                
                st.download_button(
                    label=f"📥 Download {format_choice}",
                    data=result['data'],
                    file_name=result['filename'],
                    mime="text/csv" if format_choice == "CSV" else "application/json"
                )
            else:
                st.error("Failed to export data.")

def show_past_winners():
    """Display past competition winners."""
    st.subheader("🏅 Hall of Fame - Past Winners")
    
    competition_manager = CompetitionManager()
    all_seasons = competition_manager.get_all_seasons()
    
    completed_seasons = [s for s in all_seasons if s.get('status') == 'completed']
    
    if not completed_seasons:
        st.info("No completed seasons yet.")
        return
    
    for season in reversed(completed_seasons):
        with st.expander(f"🏆 Season {season['season_number']} - {datetime.fromisoformat(season['start_date']).strftime('%B %Y')}"):
            winners = season.get('winners', [])
            
            if winners:
                for i, winner in enumerate(winners[:3], 1):
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
                    st.markdown(f"{medal} **{winner.get('username')}** - ${winner.get('total_value', 0):,.2f}")
            else:
                st.info("No winners recorded for this season.")

def show_admin_competition_panel():
    """Admin panel for managing competitions."""
    st.title("⚙️ Competition Management")
    
    # Check if user is super admin
    if not st.session_state.user_info.get('is_super_admin', False):
        st.error("🚫 Access Denied: Super Admin only")
        return
    
    competition_manager = CompetitionManager()
    cleanup_manager = DataCleanupManager()
    
    # Competition stats
    stats = competition_manager.get_competition_stats()
    
    st.subheader("📊 Competition Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Seasons", stats['total_seasons'])
    with col2:
        st.metric("Active Seasons", stats['active_seasons'])
    with col3:
        st.metric("Completed", stats['completed_seasons'])
    with col4:
        st.metric("Total Participants", stats['total_participants'])
    
    st.divider()
    
    # Current season management
    current_season = stats['current_season']
    
    if current_season:
        st.success(f"**Active: Season {current_season['season_number']}**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Started:** {datetime.fromisoformat(current_season['start_date']).strftime('%B %d, %Y')}")
            st.write(f"**Ends:** {datetime.fromisoformat(current_season['end_date']).strftime('%B %d, %Y')}")
        
        with col2:
            days_left = (datetime.fromisoformat(current_season['end_date']) - datetime.now()).days
            st.write(f"**Days Remaining:** {days_left}")
            st.write(f"**Participants:** {len(current_season.get('participants', []))}")
        
        st.divider()
        
        # End season button
        st.subheader("🏁 End Current Season")
        st.warning("This will end the competition and declare winners.")
        
        if st.button("🏁 End Season & Declare Winners", type="primary"):
            show_end_season_dialog(current_season)
    
    else:
        st.info("No active season")
        
        # Start new season
        st.subheader("🎯 Start New Season")
        
        if st.button("🚀 Start New 6-Month Competition", type="primary"):
            result = competition_manager.start_new_season()
            if result['success']:
                st.success(result['message'])
                st.rerun()
            else:
                st.error(result['message'])
    
    st.divider()
    
    # Data cleanup tools
    st.subheader("🗑️ Data Cleanup Tools")
    
    tab1, tab2 = st.tabs(["View Old Data", "Cleanup Actions"])
    
    with tab1:
        old_data = cleanup_manager.get_data_older_than(6)
        
        st.write(f"**Cutoff Date:** {datetime.fromisoformat(old_data['cutoff_date']).strftime('%B %d, %Y')}")
        st.write(f"**Trades to Delete:** {old_data['total_trades']:,}")
        st.write(f"**Affected Users:** {old_data['affected_users']}")
    
    with tab2:
        st.warning("⚠️ **Danger Zone** - These actions cannot be undone!")
        
        if st.button("🗄️ Archive Old Data"):
            result = cleanup_manager.archive_old_data("manual_archive")
            if result['success']:
                st.success(f"✅ Archived {result['stats']['total_trades']} trades")
        
        if st.button("🗑️ Delete Old Trades (6+ months)"):
            result = cleanup_manager.delete_old_trades(6)
            if result['success']:
                st.success(f"✅ Deleted {result['deleted_trades']} old trades")
        
        if st.button("💰 Reset All Users to $100k"):
            result = cleanup_manager.reset_all_users()
            if result['success']:
                st.success(f"✅ Reset {result['reset_count']} users")

def show_end_season_dialog(current_season):
    """Dialog for ending season and declaring winners."""
    st.subheader("🏆 Declare Winners")
    
    portfolio_manager = PortfolioManager()
    competition_manager = CompetitionManager()
    cleanup_manager = DataCleanupManager()
    
    # Calculate final rankings
    participants = current_season.get('participants', [])
    rankings = []
    
    for participant in participants:
        try:
            user_portfolio = portfolio_manager.get_portfolio_summary(participant['user_id'])
            if user_portfolio['success']:
                total_value = user_portfolio['portfolio']['total_value']
                rankings.append({
                    'username': participant['username'],
                    'user_id': participant['user_id'],
                    'total_value': total_value
                })
        except:
            continue
    
    rankings.sort(key=lambda x: x['total_value'], reverse=True)
    
    st.write("**Top 10 Final Rankings:**")
    for i, rank in enumerate(rankings[:10], 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
        st.write(f"{medal} {rank['username']} - ${rank['total_value']:,.2f}")
    
    st.divider()
    
    if st.button("✅ Confirm - End Season & Reset All Users", type="primary"):
        with st.spinner("Ending season..."):
            # Declare winners (top 3)
            winners = rankings[:3]
            
            # End the season
            result = competition_manager.end_current_season(winners)
            
            if result['success']:
                # Archive old data
                cleanup_manager.archive_old_data(current_season['season_id'])
                
                # Delete old trades
                cleanup_manager.delete_old_trades(6)
                
                # Reset all users
                cleanup_manager.reset_all_users(exclude_demo=True)
                
                st.success("🎉 Season ended successfully!")
                st.balloons()
                st.rerun()
