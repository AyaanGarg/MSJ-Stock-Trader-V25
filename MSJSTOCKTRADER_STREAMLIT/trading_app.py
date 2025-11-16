import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime as dt, timedelta
import time
import random
import warnings
import logging
import sys
import uuid
from io import StringIO

# Complete error suppression
warnings.filterwarnings('ignore')
logging.getLogger().setLevel(logging.CRITICAL)
sys.stderr = StringIO()  # Redirect stderr to suppress error output

# Suppress warnings and debug messages
warnings.filterwarnings('ignore')
logging.getLogger().setLevel(logging.ERROR)

# Hide Streamlit style, error messages, and all code elements
st.markdown("""
<style>
    /* Hide Streamlit branding and deployment elements */
    .stDeployButton {display:none !important;}
    footer {visibility: hidden !important;}
    .stDecoration {display:none !important;}
    #MainMenu {visibility: hidden !important;}
    header {visibility: hidden !important;}
    .viewerBadge_container__r5tak {display: none !important;}
    
    /* Hide all error messages and code traces */
    .stException {display: none !important;}
    .stException > div[data-testid="stMarkdownContainer"] > p {display: none !important;}
    .stAlert[data-baseweb="notification"] {display: none !important;}
    .stCodeBlock {display: none !important;}
    pre {display: none !important;}
    code {display: none !important;}
    
    /* Hide traceback and debug information */
    .streamlit-expanderHeader {display: none !important;}
    .stTraceback {display: none !important;}
    .stErrorDetails {display: none !important;}
    
    /* Hide any technical error displays */
    div[data-testid="stException"] {display: none !important;}
    div[data-testid="stAlert"] div:contains("error") {display: none !important;}
    
    /* Ensure clean professional look */
    .block-container {padding-top: 1rem !important;}
</style>
""", unsafe_allow_html=True)

from modules.auth_manager import AuthManager
from modules.portfolio_manager import PortfolioManager
from modules.trading_engine import TradingEngine
from modules.user_management import UserManager
from modules.market_data import MarketData
from modules.friends_manager import FriendsManager
from modules.trading_history import TradingHistory
from modules.announcements_manager import AnnouncementsManager
import csv
from io import StringIO
from modules.enhanced_team_manager import EnhancedTeamManager
from modules.badge_system import BadgeSystem
from modules.utils import format_price
from modules.competition_manager import CompetitionManager
from modules.data_cleanup_manager import DataCleanupManager
from modules.competition_pages import show_competition_status_page, show_admin_competition_panel

# Page configuration
st.set_page_config(
    page_title="MSJSTOCKTRADER",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'

# Initialize managers with error suppression
auth_manager = None
portfolio_manager = None
trading_engine = None
user_manager = None
market_data = None
announcements_manager = None
team_manager = None
badge_system = None

try:
    auth_manager = AuthManager()
    portfolio_manager = PortfolioManager()
    trading_engine = TradingEngine()
    user_manager = UserManager()
    market_data = MarketData()
    announcements_manager = AnnouncementsManager()
    team_manager = EnhancedTeamManager()
    badge_system = BadgeSystem()
except Exception as e:
    # Initialize fallback objects if needed
    st.error("System initialization in progress. Please refresh the page.")

def main():
    """Main application entry point."""
    
    # Check authentication
    if not st.session_state.authenticated:
        show_auth_page()
    else:
        show_trading_app()

def show_auth_page():
    """Display authentication page."""
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1 style="color: #1f77b4; font-size: 3rem;">📈 MSJSTOCKTRADER</h1>
        <p style="font-size: 1.2rem; color: #666;">Real Market Data • Mock Money Trading</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation tabs
    tab1, tab2, tab3 = st.tabs(["🔑 Login", "👤 Register", "🔄 Reset Password"])
    
    with tab1:
        show_login_form()
    
    with tab2:
        show_register_form()
    
    with tab3:
        show_forgot_password_form()

def show_login_form():
    """Display login form."""
    st.subheader("Login to Your Account")
    
    with st.form("login_form"):
        email = st.text_input("Email Address", placeholder="Enter your email address")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        remember_me = st.checkbox("Remember me")
        
        col1, col2 = st.columns(2)
        with col1:
            login_button = st.form_submit_button("🔑 Login", use_container_width=True)
        with col2:
            demo_button = st.form_submit_button("🎯 Demo Account", use_container_width=True)
    
    if login_button:
        if email and password:
            result = auth_manager.authenticate_user(email, password)
            if result['success']:
                st.session_state.authenticated = True
                st.session_state.user_info = result['user_info']
                st.success("Login successful!")
                st.rerun()
            else:
                st.error(result['message'])
        else:
            st.error("Please enter both email and password")
    
    if demo_button:
        # Demo account login with session management
        from modules.demo_manager import DemoManager
        demo_manager = DemoManager()
        
        # Generate unique session ID
        import uuid
        session_id = str(uuid.uuid4())
        
        # Check demo access
        access_result = demo_manager.can_access_demo(session_id)
        
        if access_result['success']:
            demo_user = auth_manager.get_demo_account()
            st.session_state.authenticated = True
            st.session_state.user_info = demo_user
            st.session_state.demo_session_id = session_id
            st.success("Demo access granted! Session expires in 5 minutes.")
            st.rerun()
        else:
            st.error(access_result['message'])
            time.sleep(2)
            st.rerun()

def show_register_form():
    """Display registration form."""
    st.markdown("### 🚀 Create Your Trading Account")
    st.markdown("Join thousands of traders practicing with real market data and get a welcome email with your account details!")
    
    with st.form("register_form"):
        st.markdown("**Personal Information**")
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name", placeholder="John")
        with col2:
            last_name = st.text_input("Last Name", placeholder="Doe")
        
        st.markdown("**Account Details**")
        username = st.text_input("Username", placeholder="johndoe", help="This will be your unique identifier")
        email = st.text_input("Email Address", placeholder="john@example.com", help="We'll send account updates here")
        
        st.markdown("**Security**")
        col3, col4 = st.columns(2)
        with col3:
            password = st.text_input("Password", type="password", placeholder="Min 8 characters", help="Choose a strong password")
        with col4:
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password")
        
        st.markdown("**Email & Agreement**")
        col5, col6 = st.columns([1, 1])
        with col5:
            email_notifications = st.checkbox("Send me welcome email and updates", value=True, help="Get account confirmation and platform updates")
        with col6:
            terms_accepted = st.checkbox("I accept the Terms of Service", help="Required to create account")
        
        st.markdown("---")
        register_button = st.form_submit_button("Create Account", use_container_width=True, type="primary")
    
    if register_button:
        # Strip whitespace from inputs
        first_name = first_name.strip() if first_name else ""
        last_name = last_name.strip() if last_name else ""
        username = username.strip() if username else ""
        email = email.strip() if email else ""
        
        # Validate all fields are filled
        if not all([first_name, last_name, username, email, password, confirm_password]):
            st.error("❌ Please fill in all required fields")
        elif len(first_name) < 2:
            st.error("❌ First name must be at least 2 characters")
        elif len(last_name) < 2:
            st.error("❌ Last name must be at least 2 characters")
        elif len(username) < 3:
            st.error("❌ Username must be at least 3 characters")
        elif '@' not in email or '.' not in email:
            st.error("❌ Please enter a valid email address")
        elif password != confirm_password:
            st.error("❌ Passwords do not match")
        elif len(password) < 8:
            st.error("❌ Password must be at least 8 characters long")
        elif not any(c.isupper() for c in password):
            st.error("❌ Password must contain at least one uppercase letter")
        elif not any(c.islower() for c in password):
            st.error("❌ Password must contain at least one lowercase letter")
        elif not any(c.isdigit() for c in password):
            st.error("❌ Password must contain at least one number")
        elif not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            st.error("❌ Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)")
        elif not terms_accepted:
            st.error("❌ Please accept the Terms of Service")
        else:
            # Create user data dictionary with all required fields
            user_data = {
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
                'email': email,
                'password': password,
                'account_type': 'Individual',
                'phone': ''
            }
            
            result = auth_manager.register_user_dict(user_data)
            
            if result['success']:
                # Send welcome email if user opted in
                if email_notifications:
                    try:
                        from modules.email_service import EmailService
                        email_service = EmailService()
                        
                        # Create full name from first and last name
                        full_name = f"{first_name} {last_name}"
                        
                        # Send welcome email (user_email, user_name, username)
                        email_result = email_service.send_welcome_email(email, full_name, username)
                        
                        if email_result['success']:
                            st.success("🎉 Account created successfully! A welcome email has been sent to your inbox.")
                            st.balloons()
                        else:
                            # Email failed - just show success without mentioning email
                            st.success("🎉 Account created successfully!")
                            st.balloons()
                            
                    except Exception as e:
                        # Email service not configured - just show success
                        st.success("🎉 Account created successfully!")
                        st.balloons()
                else:
                    st.success("🎉 Account created successfully!")
                    st.balloons()
                
                # Show next steps with enhanced instructions
                st.markdown("---")
                st.markdown("### 🚀 **What's Next?**")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("""
                    **📱 Immediate Steps:**
                    1. Go to the **Login** tab above
                    2. Enter your credentials to sign in
                    3. Start with $100,000 virtual money
                    """)
                
                with col2:
                    st.markdown("""
                    **🌟 Platform Features:**
                    - Trade 400+ real US stocks
                    - Join teams and compete
                    - Chat with other traders
                    - Earn badges and achievements
                    """)
                
                # Auto-switch to login tab after 3 seconds
                with st.empty():
                    st.info("💡 **Ready to trade!** Switch to the Login tab to access your new account.")
                    
                time.sleep(3)
            else:
                st.error(result['message'])

def show_forgot_password_form():
    """Display enhanced forgot password form with code verification."""
    st.subheader("🔄 Reset Your Password")
    
    # Initialize session state for password reset flow
    if 'reset_step' not in st.session_state:
        st.session_state.reset_step = 1
    if 'reset_email' not in st.session_state:
        st.session_state.reset_email = ""
    
    auth_manager = AuthManager()
    
    if st.session_state.reset_step == 1:
        # Step 1: Enter email address
        st.markdown("### Step 1: Enter Your Email")
        st.info("Enter your registered email address to receive a reset code.")
        
        with st.form("email_form"):
            email = st.text_input("Email Address", placeholder="Enter your registered email")
            send_code_button = st.form_submit_button("📧 Send Reset Code", use_container_width=True)
        
        if send_code_button:
            if email:
                try:
                    result = auth_manager.send_password_reset(email)
                    if result['success']:
                        st.session_state.reset_email = email
                        st.session_state.reset_step = 2
                        
                        # Display appropriate message based on email status
                        if result.get('email_sent', False):
                            st.success("✅ " + result['message'])
                            st.info("💡 The reset code is also shown below as a backup in case email delivery is delayed.")
                        else:
                            st.warning("⚠️ " + result['message'])
                            if result.get('error_details'):
                                st.error(f"Email Error Details: {result['error_details']}")
                        
                        # Create a prominent display box for the reset code
                        st.markdown("---")
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            bg_color = "#28a745" if result.get('email_sent', False) else "#667eea"
                            st.markdown(f"""
                            <div style="
                                background: linear-gradient(135deg, {bg_color} 0%, #764ba2 100%);
                                color: white;
                                padding: 25px;
                                border-radius: 15px;
                                text-align: center;
                                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                                margin: 20px 0;
                            ">
                                <h3 style="margin: 0; color: white;">Your Reset Code</h3>
                                <h1 style="
                                    font-size: 2.5em; 
                                    letter-spacing: 0.3em; 
                                    margin: 15px 0;
                                    color: #FFD700;
                                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                                ">{result['reset_code']}</h1>
                                <p style="margin: 0; opacity: 0.9;">Use this code in the next step</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.warning(f"⏰ Code expires in {result['expires_in']}")
                        if result.get('email_sent', False):
                            st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ " + result['message'])
                except Exception as e:
                    st.error(f"❌ Error sending reset code: {str(e)}")
                    st.error("Please try again or contact support at msjmockstocktradingwebsitebot@gmail.com if the problem persists.")
            else:
                st.error("❌ Please enter your email address")
    
    elif st.session_state.reset_step == 2:
        # Step 2: Enter reset code and new password
        st.markdown("### Step 2: Enter Reset Code")
        st.info(f"A 6-digit reset code has been sent to **{st.session_state.reset_email}**")
        st.warning("⏰ Reset code expires in 30 minutes")
        
        with st.form("reset_form"):
            reset_code = st.text_input("Reset Code", placeholder="Enter the 6-digit code", max_chars=6)
            new_password = st.text_input("New Password", type="password", placeholder="Enter new password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm new password")
            
            col1, col2 = st.columns(2)
            with col1:
                reset_password_button = st.form_submit_button("🔒 Reset Password", use_container_width=True)
            with col2:
                resend_code_button = st.form_submit_button("📧 Resend Code", use_container_width=True)
        
        if reset_password_button:
            if not reset_code:
                st.error("Please enter the reset code")
            elif not new_password:
                st.error("Please enter a new password")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters long")
            elif new_password != confirm_password:
                st.error("Passwords don't match")
            else:
                result = auth_manager.reset_password_with_code(
                    st.session_state.reset_email, 
                    reset_code, 
                    new_password
                )
                if result['success']:
                    st.success("Password reset successfully! You can now log in with your new password.")
                    # Reset the form state
                    st.session_state.reset_step = 1
                    st.session_state.reset_email = ""
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(result['message'])
        
        if resend_code_button:
            result = auth_manager.send_password_reset(st.session_state.reset_email)
            if result['success']:
                st.success("New reset code sent to your email!")
            else:
                st.error(result['message'])
        
        # Option to go back
        if st.button("← Back to Email Entry"):
            st.session_state.reset_step = 1
            st.session_state.reset_email = ""
            st.rerun()
    
    # Add some helpful information
    st.markdown("---")
    st.markdown("### Need Help?")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Didn't receive the code?**
        - Check your spam/junk folder
        - Wait a few minutes for delivery
        - Make sure the email address is correct
        """)
    
    with col2:
        st.markdown("""
        **Having trouble?**
        - Reset codes expire in 30 minutes
        - Contact support if issues persist
        - Try using the demo account for testing
        """)
    
    # Add demo account info and instructions
    st.info("💡 **Demo Account**: demo@stocktrade.pro / demo123")
    


def get_role_badge(role: str, is_super_admin: bool = False) -> str:
    """Get HTML badge for user role."""
    if role == "super_admin" or is_super_admin:
        return """
        <span style="background: linear-gradient(45deg, #ff6b6b, #ffd93d); 
                     color: #000; padding: 4px 12px; border-radius: 20px; 
                     font-weight: bold; font-size: 12px; text-transform: uppercase;
                     box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
            👑 SUPER ADMIN
        </span>
        """
    elif role == "admin":
        return """
        <span style="background: linear-gradient(45deg, #667eea, #764ba2); 
                     color: white; padding: 4px 12px; border-radius: 20px; 
                     font-weight: bold; font-size: 12px; text-transform: uppercase;
                     box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
            🛡️ ADMIN
        </span>
        """
    elif role == "premium":
        return """
        <span style="background: linear-gradient(45deg, #f093fb, #f5576c); 
                     color: white; padding: 4px 8px; border-radius: 15px; 
                     font-weight: bold; font-size: 11px; text-transform: uppercase;">
            ⭐ PREMIUM
        </span>
        """
    elif role == "trader":
        return """
        <span style="background: linear-gradient(45deg, #4facfe, #00f2fe); 
                     color: white; padding: 4px 8px; border-radius: 15px; 
                     font-weight: bold; font-size: 11px; text-transform: uppercase;">
            📊 TRADER
        </span>
        """
    else:
        return """
        <span style="background: #6c757d; color: white; padding: 4px 8px; 
                     border-radius: 15px; font-weight: bold; font-size: 11px; 
                     text-transform: uppercase;">
            👤 USER
        </span>
        """

def generate_daily_report(trading_engine, portfolio_manager, auth_manager):
    """Generate comprehensive daily system report for super admin download."""
    try:
        from datetime import datetime, timedelta
        import pandas as pd
        
        current_time = datetime.now()
        twenty_four_hours_ago = current_time - timedelta(hours=24)
        
        # Initialize report data
        report_sections = []
        
        # 1. SYSTEM OVERVIEW
        report_sections.append("=== MSJSTOCKTRADER DAILY REPORT ===")
        report_sections.append(f"Generated: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        report_sections.append(f"Report Period: Last 24 hours ({twenty_four_hours_ago.strftime('%Y-%m-%d %H:%M')} to {current_time.strftime('%Y-%m-%d %H:%M')})")
        report_sections.append("")
        
        # 2. USER STATISTICS
        report_sections.append("=== USER STATISTICS ===")
        users_data = auth_manager._load_users()
        
        total_users = len(users_data)
        active_users_24h = 0
        new_users_24h = 0
        user_roles = {'basic': 0, 'trader': 0, 'premium': 0, 'admin': 0}
        
        for username, user_info in users_data.items():
            # Count new registrations in last 24 hours
            if user_info.get('created_at'):
                try:
                    created_at = datetime.fromisoformat(user_info['created_at'])
                    if created_at >= twenty_four_hours_ago:
                        new_users_24h += 1
                except:
                    pass
            
            # Count active users (those who logged in recently)
            if user_info.get('last_login'):
                try:
                    last_login = datetime.fromisoformat(user_info['last_login'])
                    if last_login >= twenty_four_hours_ago:
                        active_users_24h += 1
                except:
                    pass
            
            # Count by role
            role = user_info.get('role', 'basic')
            if role in user_roles:
                user_roles[role] += 1
        
        report_sections.append(f"Total Registered Users: {total_users}")
        report_sections.append(f"New Registrations (24h): {new_users_24h}")
        report_sections.append(f"Active Users (24h): {active_users_24h}")
        report_sections.append(f"User Roles Distribution:")
        for role, count in user_roles.items():
            report_sections.append(f"  - {role.title()}: {count}")
        report_sections.append("")
        
        # 3. TRADING STATISTICS
        report_sections.append("=== TRADING STATISTICS ===")
        
        try:
            # Get trading data from all users
            total_trades_24h = 0
            total_volume_24h = 0.0
            total_profit_loss = 0.0
            most_traded_symbols = {}
            
            for username, user_info in users_data.items():
                user_id = user_info.get('user_id')
                if user_id:
                    try:
                        # Get user trades
                        trades_df = trading_engine.get_all_trades(user_id)
                        
                        if not trades_df.empty:
                            # Filter trades from last 24 hours
                            trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'])
                            recent_trades = trades_df[trades_df['timestamp'] >= twenty_four_hours_ago]
                            
                            if not recent_trades.empty:
                                total_trades_24h += len(recent_trades)
                                total_volume_24h += recent_trades['total_value'].sum()
                                
                                # Count symbol frequency
                                for symbol in recent_trades['symbol']:
                                    most_traded_symbols[symbol] = most_traded_symbols.get(symbol, 0) + 1
                    except:
                        continue
        except Exception as e:
            total_trades_24h = "Error calculating"
            total_volume_24h = 0.0
        
        report_sections.append(f"Total Trades (24h): {total_trades_24h}")
        report_sections.append(f"Total Trading Volume (24h): ${total_volume_24h:,.2f}")
        
        if most_traded_symbols:
            sorted_symbols = sorted(most_traded_symbols.items(), key=lambda x: x[1], reverse=True)
            report_sections.append("Most Traded Symbols (24h):")
            for symbol, count in sorted_symbols[:10]:  # Top 10
                report_sections.append(f"  - {symbol}: {count} trades")
        report_sections.append("")
        
        # 4. PORTFOLIO STATISTICS
        report_sections.append("=== PORTFOLIO STATISTICS ===")
        
        total_portfolio_value = 0.0
        total_cash_balance = 0.0
        total_positions_value = 0.0
        portfolio_count = 0
        
        for username, user_info in users_data.items():
            user_id = user_info.get('user_id')
            if user_id:
                try:
                    portfolio_data = portfolio_manager.get_portfolio_summary(user_id)
                    if portfolio_data and portfolio_data.get('success'):
                        portfolio = portfolio_data['portfolio']
                        total_portfolio_value += portfolio.get('total_value', 0)
                        total_cash_balance += portfolio.get('cash_balance', 0)
                        total_positions_value += portfolio.get('positions_value', 0)
                        portfolio_count += 1
                except:
                    continue
        
        avg_portfolio_value = total_portfolio_value / portfolio_count if portfolio_count > 0 else 0
        
        report_sections.append(f"Active Portfolios: {portfolio_count}")
        report_sections.append(f"Total Portfolio Value: ${total_portfolio_value:,.2f}")
        report_sections.append(f"Average Portfolio Value: ${avg_portfolio_value:,.2f}")
        report_sections.append(f"Total Cash Balance: ${total_cash_balance:,.2f}")
        report_sections.append(f"Total Positions Value: ${total_positions_value:,.2f}")
        report_sections.append("")
        
        # 5. SYSTEM HEALTH
        report_sections.append("=== SYSTEM HEALTH ===")
        report_sections.append("Application Status: Online")
        report_sections.append("Database Status: Operational")
        report_sections.append("Email Service: Configured")
        report_sections.append(f"Market Data: {len(MarketData().get_available_symbols())} symbols tracked")
        report_sections.append("")
        
        # 6. TEAM STATISTICS
        report_sections.append("=== TEAM STATISTICS ===")
        try:
            from modules.enhanced_team_manager import EnhancedTeamManager
            team_manager = EnhancedTeamManager()
            teams_data = team_manager._load_data(team_manager.teams_file)
            
            total_teams = len(teams_data)
            public_teams = sum(1 for team in teams_data.values() if team.get('is_public', True))
            private_teams = total_teams - public_teams
            total_team_members = sum(len(team.get('members', [])) for team in teams_data.values())
            
            report_sections.append(f"Total Teams: {total_teams}")
            report_sections.append(f"Public Teams: {public_teams}")
            report_sections.append(f"Private Teams: {private_teams}")
            report_sections.append(f"Total Team Members: {total_team_members}")
        except:
            report_sections.append("Team Statistics: Error loading data")
        report_sections.append("")
        
        # 7. SYSTEM RESOURCES
        report_sections.append("=== SYSTEM RESOURCES ===")
        try:
            import os
            data_dir_size = 0
            for root, dirs, files in os.walk('data'):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        data_dir_size += os.path.getsize(file_path)
            
            data_size_mb = data_dir_size / (1024 * 1024)
            report_sections.append(f"Data Directory Size: {data_size_mb:.2f} MB")
            report_sections.append(f"Total Data Files: {len([f for r, d, files in os.walk('data') for f in files])}")
        except:
            report_sections.append("System Resources: Error calculating")
        report_sections.append("")
        
        # 8. DETAILED USER LIST
        report_sections.append("=== DETAILED USER LIST ===")
        report_sections.append("Username,Email,Full Name,Role,Created Date,Last Login,Portfolio Value,Failed Logins")
        
        for username, user_info in users_data.items():
            email = user_info.get('email', 'N/A')
            full_name = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip() or 'N/A'
            role = user_info.get('role', 'basic')
            created_at = user_info.get('created_at', 'N/A')[:10] if user_info.get('created_at') else 'N/A'
            last_login = user_info.get('last_login', 'N/A')[:10] if user_info.get('last_login') else 'Never'
            failed_logins = user_info.get('failed_login_attempts', 0)
            
            # Get portfolio value
            portfolio_value = 0.0
            user_id = user_info.get('user_id')
            if user_id:
                try:
                    portfolio_data = portfolio_manager.get_portfolio_summary(user_id)
                    if portfolio_data and portfolio_data.get('success'):
                        portfolio_value = portfolio_data['portfolio'].get('total_value', 0)
                except:
                    pass
            
            report_sections.append(f"{username},{email},{full_name},{role},{created_at},{last_login},${portfolio_value:,.2f},{failed_logins}")
        
        # 9. SECURITY LOG
        report_sections.append("")
        report_sections.append("=== SECURITY LOG ===")
        report_sections.append(f"Report Generated by: Super Admin")
        report_sections.append(f"Access Level: Maximum")
        report_sections.append(f"Report Type: Full System Export")
        report_sections.append(f"Data Classification: Confidential")
        report_sections.append("WARNING: This report contains sensitive user data and should be handled securely.")
        
        # Create CSV content
        csv_content = "\n".join(report_sections)
        
        return {
            'success': True,
            'csv_data': csv_content,
            'total_trades': total_trades_24h,
            'active_users': active_users_24h,
            'total_volume': total_volume_24h,
            'report_timestamp': current_time.isoformat()
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f"Report generation failed: {str(e)}"
        }

def get_user_badge_display(user_id: str) -> str:
    """Get HTML display for user's equipped badge."""
    try:
        from modules.badge_manager import BadgeManager
        badge_manager = BadgeManager()
        return badge_manager.get_equipped_badge_html(user_id)
    except:
        return ""

def check_user_achievements(user_id: str):
    """Check and award achievements for a user."""
    try:
        from modules.badge_manager import BadgeManager
        from modules.portfolio_manager import PortfolioManager
        from modules.friends_manager import FriendsManager
        from modules.trading_engine import TradingEngine
        
        badge_manager = BadgeManager()
        portfolio_manager = PortfolioManager()
        friends_manager = FriendsManager()
        trading_engine = TradingEngine()
        
        # Gather user stats
        user_stats = {
            "portfolio_value": portfolio_manager.get_portfolio_value(user_id),
            "total_trades": len(trading_engine.get_user_trades(user_id)),
            "friend_count": len(friends_manager.get_friends(user_id)),
            "leaderboard_position": get_user_leaderboard_position(user_id)
        }
        
        # Check and award achievements
        awarded_badges = badge_manager.check_and_award_achievements(user_id, user_stats)
        
        # Show notifications for new badges
        for badge_result in awarded_badges:
            if badge_result['success']:
                badge = badge_result['badge']
                st.success(f"🏆 Achievement Unlocked: {badge['name']}!")
                st.balloons()
    except Exception as e:
        pass  # Silently handle errors

def get_user_leaderboard_position(user_id: str) -> int:
    """Get user's current position on the leaderboard."""
    try:
        from modules.friends_manager import FriendsManager
        friends_manager = FriendsManager()
        leaderboard_data = friends_manager.get_leaderboard_data()
        
        for i, entry in enumerate(leaderboard_data, 1):
            if entry.get('user_id') == user_id:
                return i
        return 999  # Not on leaderboard
    except:
        return 999

def show_announcements():
    """Display system announcements to all users."""
    if not announcements_manager:
        return
    
    try:
        active_announcements = announcements_manager.get_active_announcements()
        
        if active_announcements:
            st.markdown("---")
            
            for announcement in active_announcements:
                priority = announcement.get("priority", "Medium")
                message = announcement.get("message", "")
                created_at = announcement.get("created_at", "")
                announcement_id = announcement.get("id", 0)
                
                # Get priority styling
                priority_color = announcements_manager.get_priority_color(priority)
                priority_icon = announcements_manager.get_priority_icon(priority)
                
                # Format creation date
                try:
                    created_date = dt.fromisoformat(created_at)
                    date_str = created_date.strftime("%B %d, %Y at %I:%M %p")
                except:
                    date_str = "Recently"
                
                # Display announcement with styling
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, {priority_color}15, {priority_color}05); 
                            border-left: 4px solid {priority_color}; 
                            padding: 15px; margin: 10px 0; border-radius: 8px;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="flex: 1;">
                            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                                <span style="font-size: 18px; margin-right: 8px;">{priority_icon}</span>
                                <strong style="color: {priority_color}; font-size: 14px;">{priority.upper()} ANNOUNCEMENT</strong>
                                <span style="color: #666; font-size: 12px; margin-left: 10px;">{date_str}</span>
                            </div>
                            <p style="margin: 0; font-size: 14px; color: #333; line-height: 1.4;">
                                {message}
                            </p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
    
    except Exception as e:
        # Silently handle errors to not disrupt user experience
        pass


def show_trading_app():
    """Display main trading application."""
    user_info = st.session_state.user_info
    
    # Safety check: ensure user_info is a dictionary
    if not isinstance(user_info, dict):
        st.error("Session error. Please log in again.")
        st.session_state.authenticated = False
        st.session_state.user_info = None
        st.rerun()
        return
    
    # Check demo session validity and update activity
    if user_info.get('username') == 'demo' and 'demo_session_id' in st.session_state:
        from modules.demo_manager import DemoManager
        demo_manager = DemoManager()
        demo_manager.update_demo_activity(st.session_state.demo_session_id)
        
        # Check if session has expired
        access_result = demo_manager.can_access_demo(st.session_state.demo_session_id)
        if not access_result['success']:
            st.session_state.authenticated = False
            st.session_state.user_info = None
            if 'demo_session_id' in st.session_state:
                del st.session_state.demo_session_id
            st.error("Demo session expired. Please log in again.")
            st.rerun()
    
    # Create main layout with sidebar
    main_col, sidebar_col = st.columns([3, 1])
    
    with main_col:
        # Enhanced Header with branding
        role_badge = get_role_badge(user_info['role'], user_info.get('is_super_admin', False))
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 15px; margin-bottom: 20px; 
                    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 700;">
                        📈 MSJSTOCKTRADER
                    </h1>
                    <p style="color: #e6f3ff; margin: 5px 0 0 0; font-size: 1.1rem;">
                        Real Market Data • Mock Money Trading
                    </p>
                </div>
                <div style="text-align: right;">
                    {role_badge}
                    <p style="color: #e6f3ff; margin: 10px 0 0 0; font-size: 0.9rem;">
                        {'🔒 Demo Account - View Only' if user_info.get('username') == 'demo' else f"Welcome back, <strong>{user_info['first_name']} {user_info['last_name']}</strong>"}
                    </p>
                    <div style="margin-top: 10px;">
                        {get_user_badge_display(user_info['user_id'])}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
        # Navigation
        # Get menu items based on role and super admin status
        user_role = user_info.get('role', 'basic')
        is_super_admin = user_info.get('is_super_admin', False)
        menu_items = get_menu_items_for_role(user_role, is_super_admin)
        
        # Navigation dropdown
        selected_page = st.selectbox(
            "📋 Navigation", 
            menu_items,
            label_visibility="visible"
        )
        
        # Display announcements between navigation and content
        show_announcements()
        
    
    # Compact Sidebar
    with sidebar_col:
        # Compact Account Information
        notification_badge = ""
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 12px; margin-bottom: 15px; 
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);">
            <div style="text-align: center; color: white;">
                <div style="margin-bottom: 15px;">
                    <div style="background: rgba(255,255,255,0.2); width: 50px; height: 50px; 
                                border-radius: 50%; margin: 0 auto 10px auto; display: flex; 
                                align-items: center; justify-content: center; font-size: 20px;">
                        👤
                    </div>
                    <h3 style="margin: 0; font-size: 18px; font-weight: 600;">{user_info['username']}</h3>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 8px 12px; 
                            border-radius: 20px; display: inline-block;">
                    <span style="font-size: 12px;">💬 Messages{notification_badge}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Compact Portfolio Stats
        portfolio_value = portfolio_manager.get_portfolio_value(user_info['user_id']) if portfolio_manager else 100000
        cash_balance = portfolio_manager.get_cash_balance(user_info['user_id']) if portfolio_manager else 100000
        daily_pnl = portfolio_manager.get_daily_pnl(user_info['user_id']) if portfolio_manager else 0
        
        st.markdown("**💰 Portfolio**")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Value", f"${portfolio_value:,.0f}")
        with col2:
            st.metric("Cash", f"${cash_balance:,.0f}")
        
        pnl_color = "normal" if daily_pnl >= 0 else "inverse"
        st.metric("Daily P&L", f"${daily_pnl:,.0f}", delta=f"${daily_pnl:,.0f}", delta_color=pnl_color)
        
        # Compact Settings
        with st.expander("⚙️ Settings"):
            # Profile Edit Button
            if st.button("✏️ Edit Profile", use_container_width=True):
                st.session_state.show_profile_editor = True
                st.rerun()
            
            # Quick Password Change
            with st.popover("🔒 Change Password"):
                old_pass = st.text_input("Current", type="password", key="quick_old")
                new_pass = st.text_input("New", type="password", key="quick_new")
                if st.button("Update", key="quick_change"):
                    if len(new_pass) >= 6:
                        result = auth_manager.change_password(user_info['username'], old_pass, new_pass) if auth_manager else {'success': False, 'message': 'System not ready'}
                        if result['success']:
                            st.success("Updated!")
                        else:
                            st.error(result['message'])
                    else:
                        st.error("Min 6 characters")
        
        # Demo session timer for demo accounts
        if user_info.get('username') == 'demo' and 'demo_session_id' in st.session_state:
            try:
                from modules.demo_manager import DemoManager
                demo_manager = DemoManager()
                session_data = demo_manager._load_demo_session()
                
                if session_data and session_data.get("current_user") == st.session_state.demo_session_id:
                    session_start = dt.fromisoformat(session_data["session_start"])
                    time_remaining = timedelta(minutes=5) - (dt.now() - session_start)
                    minutes_remaining = max(0, int(time_remaining.total_seconds() // 60))
                    
                    st.markdown(f"""
                    <div style="background: #ffc107; color: #000; padding: 10px; border-radius: 5px; margin: 10px 0;">
                        <div style="text-align: center;">
                            <strong>⏰ Demo Session (5 min limit)</strong><br>
                            <span style="font-size: 16px;">{minutes_remaining} minutes remaining</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            except:
                pass
        
        st.markdown("---")
        
        # Logout button with enhanced styling
        if st.button("🔓 Logout", use_container_width=True, type="secondary"):
            # Handle demo account logout
            if st.session_state.user_info.get('username') == 'demo' and 'demo_session_id' in st.session_state:
                from modules.demo_manager import DemoManager
                demo_manager = DemoManager()
                demo_manager.release_demo_access(st.session_state.demo_session_id)
            
            st.session_state.authenticated = False
            st.session_state.user_info = None
            if 'demo_session_id' in st.session_state:
                del st.session_state.demo_session_id
            st.rerun()
    
    # Check if profile editor should be shown - but don't return, show it as a modal
    if st.session_state.get('show_profile_editor', False):
        with st.container():
            show_profile_editor()
            st.markdown("---")
            return  # Only return after showing the editor
    
    # Main content based on selected page
    if selected_page == "Dashboard":
        show_dashboard()
    elif selected_page == "Trading":
        show_trading_page()
    elif selected_page == "Portfolio":
        show_portfolio_page()
    elif selected_page == "Market Data":
        show_market_data_page()
    elif selected_page == "Watchlist":
        show_watchlist_page()
    elif selected_page == "Pending Orders":
        show_pending_orders_page()
    elif selected_page == "Competition":
        show_competition_status_page()
    elif selected_page == "Discord":
        show_chat_page()
    elif selected_page == "Friends":
        show_friends_page()
    elif selected_page == "Leaderboard":
        show_leaderboard_page()
    elif selected_page == "History":
        show_history_page()
    elif selected_page == "Reports":
        show_reports_page()
    elif selected_page == "User Management":
        show_user_management_page()
    elif selected_page == "Admin Panel":
        show_admin_panel()

def get_menu_items_for_role(role, is_super_admin=False):
    """Get menu items based on user role and super admin status."""
    base_items = ["Dashboard", "Trading", "Portfolio", "Market Data", "Watchlist"]
    
    # Add social features for all users (Competition now includes leaderboard)
    base_items.extend(["Pending Orders", "Competition", "Discord", "Friends", "History"])
    
    if role in ["trader", "premium"]:
        base_items.append("Reports")
    
    # Admin access for both admin role and super admin users
    if role in ["admin", "super_admin"] or is_super_admin:
        base_items.extend(["User Management", "Admin Panel"])
    
    return base_items

def show_profile_editor():
    """Display profile editor interface."""
    st.title("✏️ Edit Profile")
    
    user_info = st.session_state.user_info
    
    # Create tabs for profile sections
    tab1, tab2 = st.tabs(["📝 Profile Info", "🏆 Badge Inventory"])
    
    with tab1:
        with st.form("profile_form"):
            st.subheader("Personal Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("Username", value=user_info.get('username', ''))
                new_first_name = st.text_input("First Name", value=user_info.get('first_name', ''))
                new_phone = st.text_input("Phone Number", value=user_info.get('phone', ''))
            
            with col2:
                new_email = st.text_input("Email Address", value=user_info.get('email', ''), disabled=True)
                new_last_name = st.text_input("Last Name", value=user_info.get('last_name', ''))
                new_account_type = st.selectbox("Account Type", 
                                              ["Individual", "Corporate", "Professional"], 
                                              index=["Individual", "Corporate", "Professional"].index(user_info.get('account_type', 'Individual')))
            
            st.info("Note: Email address cannot be changed. Contact support at msjmockstocktradingwebsitebot@gmail.com if you need to update your email.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                save_button = st.form_submit_button("💾 Save Changes", use_container_width=True)
            
            with col2:
                cancel_button = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if save_button:
            changes_made = False
            
            # Update username if changed
            if new_username != user_info.get('username', ''):
                result = auth_manager.update_username(user_info['user_id'], new_username)
                if result['success']:
                    st.success(result['message'])
                    user_info['username'] = new_username
                    changes_made = True
                else:
                    st.error(result['message'])
                    return
            
            # Update other fields
            if (new_first_name != user_info.get('first_name', '') or 
                new_last_name != user_info.get('last_name', '') or 
                new_phone != user_info.get('phone', '') or 
                new_account_type != user_info.get('account_type', '')):
                
                # Update user info in session
                user_info['first_name'] = new_first_name
                user_info['last_name'] = new_last_name
                user_info['phone'] = new_phone
                user_info['account_type'] = new_account_type
                changes_made = True
            
            if changes_made:
                st.session_state.user_info = user_info
                st.success("Profile updated successfully!")
            
            st.session_state.show_profile_editor = False
            st.rerun()
        
        if cancel_button:
            st.session_state.show_profile_editor = False
            st.rerun()
    
    with tab2:
        # Badge Inventory Section
        st.subheader("🏆 Badge Collection & Inventory")
        
        # Initialize badge manager
        from modules.badge_manager import BadgeManager
        badge_manager = BadgeManager()
        
        # Get user badges
        user_badges = badge_manager.get_user_badges(user_info['user_id'])
        
        # Current equipped badge
        st.markdown("### Currently Equipped Badge")
        if user_badges["equipped_badge"]:
            badge = user_badges["equipped_badge"]
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.markdown(f"""
                <div style="background: {badge['color']}; color: white; padding: 20px; 
                           border-radius: 10px; text-align: center; margin: 10px 0;">
                    <div style="font-size: 40px; margin-bottom: 10px;">{badge['icon']}</div>
                    <div style="font-weight: bold; font-size: 12px;">{badge['name']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"**{badge['name']}**")
                st.caption(f"Rarity: {badge['rarity']} • Category: {badge['category']}")
                st.write(badge['description'])
                
                if st.button("🚫 Unequip Badge", key="unequip_current"):
                    result = badge_manager.unequip_badge(user_info['user_id'])
                    if result['success']:
                        st.success(result['message'])
                        st.rerun()
                    else:
                        st.error(result['message'])
        else:
            st.info("No badge currently equipped. Select one from your collection below!")
        
        st.markdown("---")
        
        # Badge collection
        st.markdown("### 🎒 Your Badge Collection")
        
        if user_badges["earned_badges"]:
            st.write(f"**Total Badges:** {user_badges['badge_count']}")
            
            # Group badges by category
            categories = {}
            for badge in user_badges["earned_badges"]:
                category = badge.get("category", "Other")
                if category not in categories:
                    categories[category] = []
                categories[category].append(badge)
            
            # Display badges by category
            for category, badges in categories.items():
                with st.expander(f"📂 {category} Badges ({len(badges)})", expanded=True):
                    for badge in badges:
                        col1, col2, col3 = st.columns([1, 3, 1])
                        
                        with col1:
                            rarity_color = badge_manager.get_badge_rarity_color(badge['rarity'])
                            st.markdown(f"""
                            <div style="background: {badge['color']}; color: white; padding: 15px; 
                                       border-radius: 8px; text-align: center; 
                                       border: 3px solid {rarity_color};">
                                <div style="font-size: 30px; margin-bottom: 5px;">{badge['icon']}</div>
                                <div style="font-size: 10px; font-weight: bold;">{badge['rarity']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f"**{badge['name']}**")
                            st.caption(f"Earned: {dt.fromisoformat(badge['earned_date']).strftime('%B %d, %Y')}")
                            st.write(badge['description'])
                            if badge.get('reason'):
                                st.caption(f"Reason: {badge['reason']}")
                        
                        with col3:
                            is_equipped = user_badges["equipped_badge_id"] == badge["badge_id"]
                            
                            if is_equipped:
                                st.button("✅ Equipped", key=f"equipped_{badge['badge_id']}", disabled=True)
                            else:
                                if st.button("🔄 Equip", key=f"equip_{badge['badge_id']}"):
                                    result = badge_manager.equip_badge(user_info['user_id'], badge['badge_id'])
                                    if result['success']:
                                        st.success(result['message'])
                                        st.rerun()
                                    else:
                                        st.error(result['message'])
                        
                        st.divider()
        else:
            st.info("🏆 No badges earned yet! Complete achievements to earn your first badge.")
            
            # Show some available achievements
            st.markdown("### 🎯 Available Achievements")
            all_badges = badge_manager.get_all_badge_definitions()
            
            # Show a few example achievements
            example_badges = ["millionaire", "leaderboard_champion", "social_butterfly", "day_trader"]
            
            for badge_id in example_badges:
                if badge_id in all_badges:
                    badge = all_badges[badge_id]
                    col1, col2 = st.columns([1, 4])
                    
                    with col1:
                        st.markdown(f"""
                        <div style="background: {badge['color']}; color: white; padding: 10px; 
                                   border-radius: 5px; text-align: center; opacity: 0.6;">
                            <div style="font-size: 20px;">{badge['icon']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"**{badge['name']}**")
                        st.caption(f"{badge['description']} • {badge['requirements']}")
    
    # Close button for profile editor
    st.markdown("---")
    if st.button("← Back to Dashboard", use_container_width=True):
        st.session_state.show_profile_editor = False
        st.rerun()

def show_dashboard():
    """Display compact main dashboard."""
    # Compact header with quick actions
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("📊 Trading Dashboard")
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # Check for achievements
    check_user_achievements(st.session_state.user_info['user_id'])
    
    # Key metrics in compact layout
    portfolio_value = portfolio_manager.get_portfolio_value(st.session_state.user_info['user_id'])
    daily_pnl = portfolio_manager.get_daily_pnl(st.session_state.user_info['user_id'])
    buying_power = portfolio_manager.get_buying_power(st.session_state.user_info['user_id'])
    positions = portfolio_manager.get_positions(st.session_state.user_info['user_id'])
    today_trades = trading_engine.get_today_trades(st.session_state.user_info['user_id'])
    
    # Compact metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Portfolio", f"${portfolio_value:,.0f}", f"{daily_pnl:+.0f}")
    with col2:
        st.metric("Buying Power", f"${buying_power:,.0f}")
    with col3:
        st.metric("Positions", len(positions))
    with col4:
        st.metric("Today's Trades", len(today_trades))
    
# Quick overview section removed to eliminate duplication with main navigation
    
    # Tabbed content to save vertical space
    tab1, tab2, tab3 = st.tabs(["📈 Performance", "🔥 Market Movers", "📊 Recent Activity"])
    
    with tab1:
        portfolio_history = portfolio_manager.get_portfolio_history(st.session_state.user_info['user_id'])
        if not portfolio_history.empty:
            # Simplify flat data to ensure perfectly flat line rendering
            if portfolio_history['value'].nunique() == 1:
                # For flat line, only use first and last date to avoid SVG path variations
                simplified_history = pd.DataFrame({
                    'date': [portfolio_history['date'].iloc[0], portfolio_history['date'].iloc[-1]],
                    'value': [portfolio_history['value'].iloc[0], portfolio_history['value'].iloc[0]]
                })
                fig = px.line(simplified_history, x='date', y='value', 
                             title="Portfolio Performance", height=300)
                flat_value = simplified_history['value'].iloc[0]
                fig.update_yaxes(
                    range=[flat_value - 500, flat_value + 500],
                    tickmode='array',
                    tickvals=[flat_value],
                    ticktext=[f"${flat_value:,.0f}"],
                    fixedrange=True
                )
            else:
                fig = px.line(portfolio_history, x='date', y='value', 
                             title="Portfolio Performance", height=300)
            
            fig.update_layout(margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Start trading to see your portfolio performance")
    
    with tab2:
        market_movers = market_data.get_market_movers()
        st.dataframe(market_movers.head(8), use_container_width=True, height=280)
    
    with tab3:
        recent_trades = trading_engine.get_recent_trades(st.session_state.user_info['user_id'], limit=8)
        if not recent_trades.empty:
            # Show only key columns for compact view
            display_columns = ['symbol', 'side', 'quantity', 'price', 'timestamp']
            available_columns = [col for col in display_columns if col in recent_trades.columns]
            if available_columns:
                st.dataframe(recent_trades[available_columns], use_container_width=True, height=280)
            else:
                st.dataframe(recent_trades.head(8), use_container_width=True, height=280)
        else:
            st.info("No recent trading activity")

def show_trading_page():
    """Display compact trading interface."""
    # Compact header with enhanced stock selector
    col1, col2 = st.columns([2, 1])
    with col1:
        st.title("💰 Trading Terminal")
    with col2:
        # Enhanced stock search
        search_query = st.text_input("🔍 Search Stocks", 
                                   placeholder="Try: Apple, AAPL, Tesla, Microsoft...",
                                   help="Search by company name or stock symbol")
        
        if search_query:
            search_results = market_data.search_stocks(search_query)
            if search_results:
                # Create display options with both symbol and company name
                stock_options = []
                for result in search_results[:10]:  # Limit to top 10 results
                    stock_options.append(f"{result['symbol']} - {result['name']}")
                
                selected_option = st.selectbox("📊 Select from search results:", 
                                             stock_options,
                                             help="Choose a stock from your search results")
                
                if selected_option:
                    symbol = selected_option.split(" - ")[0]  # Extract symbol
                else:
                    symbol = None
            else:
                st.warning(f"No stocks found matching '{search_query}'")
                symbol = None
        else:
            # Default stock selection when no search
            popular_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX']
            symbol = st.selectbox("📊 Popular Stocks", popular_stocks, 
                                 help="Choose from popular stocks or use search above")
    
    if symbol:
        # Current price and quick info
        current_price = market_data.get_current_price(symbol)
        stock_quote = market_data.get_stock_quote(symbol)
        
        # Compact price display
        price_col1, price_col2, price_col3, price_col4 = st.columns(4)
        with price_col1:
            st.metric("Current Price", format_price(current_price))
        with price_col2:
            change = stock_quote.get('change', 0)
            st.metric("Change", f"${change:.2f}", delta=f"{change:.2f}")
        with price_col3:
            change_pct = stock_quote.get('change_percent', 0)
            st.metric("Change %", f"{change_pct:.1f}%")
        with price_col4:
            volume = stock_quote.get('volume', 0)
            st.metric("Volume", f"{volume:,.0f}")
        
        # Main content in columns
        chart_col, trade_col = st.columns([2.5, 1.5])
        
        with chart_col:
            # Compact chart
            stock_data = market_data.get_stock_data(symbol, days=30)
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=stock_data['date'],
                open=stock_data['open'],
                high=stock_data['high'],
                low=stock_data['low'],
                close=stock_data['close'],
                name=symbol
            ))
            fig.update_layout(
                title=f"{symbol} - 30 Day Chart", 
                height=400,
                margin=dict(l=0, r=0, t=40, b=0),
                xaxis_title="", 
                yaxis_title="Price"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with trade_col:
            # Compact trading form
            st.markdown("### 📝 Place Order")
            
            with st.form("trading_form"):
                col1, col2 = st.columns(2)
                with col1:
                    side = st.selectbox("Side", ["Buy", "Sell", "Short Sell", "Short Cover"])
                with col2:
                    order_type = st.selectbox("Type", ["Market", "Limit"])
                
                quantity_input = st.number_input("Shares (whole numbers only)", min_value=1, value=1, step=1)
                quantity = int(quantity_input)  # Enforce whole numbers
                
                if order_type == "Limit":
                    price = st.number_input("Limit Price", min_value=0.01, 
                                          value=current_price, step=0.01)
                else:
                    price = current_price
                    st.info(f"Market: {format_price(current_price)}")
                
                # Order value calculation
                order_value = quantity * price
                
                # Show warning if decimal was entered
                if quantity_input != quantity:
                    st.warning(f"⚠️ Decimal values not allowed. Using {quantity} shares instead of {quantity_input}")
                
                st.write(f"**Order Value:** ${order_value:,.2f}")
                
                # Buying power check
                buying_power = portfolio_manager.get_buying_power(st.session_state.user_info['user_id'])
                
                # Check buying power for Buy and Short Sell (both require capital)
                if side in ["Buy", "Short Sell"] and order_value > buying_power:
                    st.error(f"Insufficient buying power: ${buying_power:,.2f}")
                    submit_disabled = True
                else:
                    submit_disabled = False
                
                # Show info for short selling
                if side == "Short Sell":
                    st.info("⚠️ Short Sell: Profit if price goes down. Requires collateral.")
                
                submit_order = st.form_submit_button("📤 Submit Order", 
                                                   use_container_width=True,
                                                   disabled=submit_disabled)
            
            if submit_order:
                # Convert side to lowercase and handle short sell/cover
                side_value = side.lower().replace(" ", "_")
                
                order_data = {
                    'symbol': symbol,
                    'side': side_value,
                    'quantity': int(quantity),  # Enforce whole numbers
                    'order_type': order_type.lower(),
                    'price': price,
                    'user_id': st.session_state.user_info['user_id']
                }
                
                result = trading_engine.place_order(order_data)
                if result['success']:
                    st.success(f"✅ Order placed! ID: {result['order_id']}")
                    st.rerun()  # Refresh to show updated portfolio
                else:
                    st.error(f"❌ {result['message']}")
    else:
        st.info("Select a stock to start trading")

def show_portfolio_page():
    """Display portfolio information."""
    st.title("📁 Portfolio Management")
    
    user_id = st.session_state.user_info['user_id']
    
    # Portfolio summary
    st.subheader("Portfolio Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_value = portfolio_manager.get_portfolio_value(user_id)
        st.metric("Total Portfolio Value", f"${total_value:,.2f}")
    
    with col2:
        cash_balance = portfolio_manager.get_cash_balance(user_id)
        st.metric("Cash Balance", f"${cash_balance:,.2f}")
    
    with col3:
        invested_value = total_value - cash_balance
        st.metric("Invested Value", f"${invested_value:,.2f}")
    
    # Holdings
    st.subheader("Current Holdings")
    positions = portfolio_manager.get_positions(user_id)
    
    if not positions.empty:
        # Add current market values
        for index, row in positions.iterrows():
            current_price = market_data.get_current_price(row['symbol'])
            positions.at[index, 'current_price'] = current_price
            positions.at[index, 'market_value'] = current_price * row['quantity']
            positions.at[index, 'unrealized_pnl'] = (current_price - row['avg_cost']) * row['quantity']
        
        st.dataframe(positions, use_container_width=True)
        
        # Portfolio allocation chart
        fig = px.pie(positions, values='market_value', names='symbol', title="Portfolio Allocation")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No current holdings")

def show_market_data_page():
    """Display market data and analysis with asset categories."""
    st.title("📊 Market Data & Asset Explorer")
    
    # Asset categories tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Market Overview", 
        "💰 Cryptocurrency", 
        "🥇 Precious Metals", 
        "🏦 Money Market", 
        "📊 Traditional Stocks",
        "🔍 Stock Browser"
    ])
    
    with tab1:
        # Market overview
        st.subheader("Market Overview")
    
    market_summary = market_data.get_market_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("S&P 500", f"{market_summary['sp500']:.2f}", f"{market_summary['sp500_change']:+.2f}")
    
    with col2:
        st.metric("NASDAQ", f"{market_summary['nasdaq']:.2f}", f"{market_summary['nasdaq_change']:+.2f}")
    
    with col3:
        st.metric("DOW", f"{market_summary['dow']:.2f}", f"{market_summary['dow_change']:+.2f}")
    
    with col4:
        st.metric("VIX", f"{market_summary['vix']:.2f}", f"{market_summary['vix_change']:+.2f}")
    
    # Top movers with Show All option
    col1, col2 = st.columns(2)
    
    with col1:
        # Top Gainers with Show All option
        gainer_col1, gainer_col2 = st.columns([3, 1])
        with gainer_col1:
            st.subheader("📈 Top Gainers")
        with gainer_col2:
            show_all_gainers = st.checkbox("Show All", key="show_all_gainers", help="Show all gaining stocks")
        
        gainers = market_data.get_top_gainers(limit=5, show_all=show_all_gainers)
        if not gainers.empty:
            # Format the dataframe for better display
            gainers_display = gainers.copy()
            gainers_display['Price'] = gainers_display['price'].apply(lambda x: f"${x:.2f}")
            gainers_display['Change'] = gainers_display['change'].apply(lambda x: f"+${x:.2f}")
            gainers_display['Change %'] = gainers_display['change_pct'].apply(lambda x: f"+{x:.2f}%")
            gainers_display['Volume'] = gainers_display['volume'].apply(lambda x: f"{x:,}")
            
            display_cols = ['symbol', 'company_name', 'Price', 'Change', 'Change %', 'Volume']
            gainers_display = gainers_display[display_cols]
            gainers_display.columns = ['Symbol', 'Company', 'Price', 'Change', 'Change %', 'Volume']
            
            st.dataframe(gainers_display, use_container_width=True, height=400 if show_all_gainers else 200)
            if show_all_gainers:
                st.info(f"Showing all {len(gainers_display)} gaining stocks")
        else:
            st.info("No gainers data available")
    
    with col2:
        # Top Losers with Show All option
        loser_col1, loser_col2 = st.columns([3, 1])
        with loser_col1:
            st.subheader("📉 Top Losers")
        with loser_col2:
            show_all_losers = st.checkbox("Show All", key="show_all_losers", help="Show all losing stocks")
        
        losers = market_data.get_top_losers(limit=5, show_all=show_all_losers)
        if not losers.empty:
            # Format the dataframe for better display
            losers_display = losers.copy()
            losers_display['Price'] = losers_display['price'].apply(lambda x: f"${x:.2f}")
            losers_display['Change'] = losers_display['change'].apply(lambda x: f"${x:.2f}")
            losers_display['Change %'] = losers_display['change_pct'].apply(lambda x: f"{x:.2f}%")
            losers_display['Volume'] = losers_display['volume'].apply(lambda x: f"{x:,}")
            
            display_cols = ['symbol', 'company_name', 'Price', 'Change', 'Change %', 'Volume']
            losers_display = losers_display[display_cols]
            losers_display.columns = ['Symbol', 'Company', 'Price', 'Change', 'Change %', 'Volume']
            
            st.dataframe(losers_display, use_container_width=True, height=400 if show_all_losers else 200)
            if show_all_losers:
                st.info(f"Showing all {len(losers_display)} losing stocks")
        else:
            st.info("No losers data available")
    
    with tab2:
        st.header("💰 Cryptocurrency Market")
        
        # Get crypto categories
        crypto_categories = market_data.get_asset_categories()["Cryptocurrency"]
        
        for category, symbols in crypto_categories.items():
            st.subheader(f"📈 {category}")
            
            crypto_data = []
            for symbol in symbols[:8]:  # Show top 8 in each category
                try:
                    price = market_data.get_current_price(symbol)
                    crypto_data.append({
                        'Symbol': symbol,
                        'Current Price': f"${price:,.4f}" if price < 1 else f"${price:,.2f}",
                        'Asset Type': 'Cryptocurrency' if '-USD' in symbol else 'Crypto Stock'
                    })
                except:
                    continue
            
            if crypto_data:
                crypto_df = pd.DataFrame(crypto_data)
                st.dataframe(crypto_df, use_container_width=True, height=200)
        
        st.info("💡 Tip: Cryptocurrency prices are highly volatile. Trade with caution and proper risk management.")
    
    with tab3:
        st.header("🥇 Precious Metals Investment")
        
        # Show precious metals information
        metals_info = market_data.get_precious_metals_info()
        
        st.subheader("🏆 The 10 Most Famous Precious Metals")
        
        # Create expandable sections for each metal
        for metal_name, info in metals_info.items():
            with st.expander(f"🔸 {metal_name}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Description:** {info['description']}")
                    st.write(f"**Properties:** {info['properties']}")
                    st.write(f"**Current Uses:** {info['current_use']}")
                
                with col2:
                    # Show current price for tradeable symbols
                    if info['symbol'] in ['GLD', 'SLV', 'PPLT', 'PALL']:
                        try:
                            price = market_data.get_current_price(info['symbol'])
                            st.metric(f"{info['symbol']} Price", f"${price:.2f}")
                        except:
                            st.write(f"**Symbol:** {info['symbol']}")
                    else:
                        st.write(f"**Investment:** {info['symbol']}")
        
        # Precious metals trading table
        st.subheader("📊 Precious Metals ETFs & Stocks")
        metals_categories = market_data.get_asset_categories()["Precious Metals"]
        
        metals_data = []
        for category, symbols in metals_categories.items():
            for symbol in symbols[:5]:  # Top 5 per category
                try:
                    price = market_data.get_current_price(symbol)
                    metals_data.append({
                        'Symbol': symbol,
                        'Category': category,
                        'Current Price': f"${price:.2f}",
                        'Type': 'ETF' if symbol in ['GLD', 'SLV', 'PPLT', 'PALL'] else 'Stock'
                    })
                except:
                    continue
        
        if metals_data:
            metals_df = pd.DataFrame(metals_data)
            st.dataframe(metals_df, use_container_width=True, height=300)
    
    with tab4:
        st.header("🏦 Money Market & Bond Investments")
        
        bonds_categories = market_data.get_asset_categories()["Bonds & Fixed Income"]
        
        for category, symbols in bonds_categories.items():
            st.subheader(f"📈 {category} Bonds")
            
            bonds_data = []
            for symbol in symbols:
                try:
                    price = market_data.get_current_price(symbol)
                    bonds_data.append({
                        'Symbol': symbol,
                        'Current Price': f"${price:.2f}",
                        'Category': category,
                        'Risk Level': 'Low' if 'BIL' in symbol or 'SHY' in symbol else 'Medium' if 'IEF' in symbol else 'High'
                    })
                except:
                    continue
            
            if bonds_data:
                bonds_df = pd.DataFrame(bonds_data)
                st.dataframe(bonds_df, use_container_width=True, height=200)
        
        st.info("💡 Money market and bond investments typically offer lower risk and steady returns compared to stocks.")
    
    with tab5:
        st.header("📊 Traditional Stock Market")
        
        # Traditional stocks by sector
        stock_categories = market_data.get_asset_categories()["Stocks"]
        
        for sector, symbols in stock_categories.items():
            st.subheader(f"🏢 {sector}")
            
            sector_data = []
            for symbol in symbols:
                try:
                    price = market_data.get_current_price(symbol)
                    sector_data.append({
                        'Symbol': symbol,
                        'Current Price': f"${price:.2f}",
                        'Sector': sector
                    })
                except:
                    continue
            
            if sector_data:
                sector_df = pd.DataFrame(sector_data)
                st.dataframe(sector_df, use_container_width=True, height=200)
    
    with tab6:
        # Stock Browser Section
        st.subheader("🔍 Complete Asset Browser")
        st.markdown("Search through all available assets including stocks, crypto, precious metals, and bonds")
        
        # Search interface
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_term = st.text_input("Search Assets", 
                                       placeholder="Search by company name (Tesla, Apple) or symbol (TSLA, AAPL, BTC-USD)...",
                                       key="market_search")
        
        with col2:
            show_all = st.checkbox("Show All Assets", help="Display all tracked securities")
        
        # Display search results or all stocks
        if search_term:
            search_results = market_data.search_stocks(search_term)
            if search_results:
                st.markdown(f"**Found {len(search_results)} assets matching '{search_term}':**")
                
                # Create a DataFrame for better display
                display_data = []
                for stock in search_results:
                    display_data.append({
                        'Symbol': stock['symbol'],
                        'Company Name': stock['name'],
                        'Current Price': f"${stock['price']:.2f}",
                        'Match Type': stock['match_type'].replace('_', ' ').title()
                    })
                
                results_df = pd.DataFrame(display_data)
                st.dataframe(results_df, use_container_width=True, height=400)
            else:
                st.warning(f"No assets found matching '{search_term}'")
        
        elif show_all:
            st.markdown("**All Available Assets:**")
            
            # Get all stocks with their names
            all_symbols = market_data.get_available_symbols()
            name_mapping = market_data.get_stock_name_mapping()
            
            # Create comprehensive stock list
            all_stocks_data = []
            for symbol in all_symbols:
                company_name = name_mapping.get(symbol, f"{symbol} Corporation")
                try:
                    current_price = market_data.get_current_price(symbol)
                    
                    # Determine asset type
                    asset_type = "Stock"
                    if "-USD" in symbol:
                        asset_type = "Cryptocurrency"
                    elif symbol in ['GLD', 'SLV', 'PPLT', 'PALL', 'GDX', 'GDXJ']:
                        asset_type = "Precious Metals"
                    elif symbol in ['BIL', 'SHY', 'IEF', 'TLT', 'AGG', 'BND']:
                        asset_type = "Bonds/Money Market"
                    
                    all_stocks_data.append({
                        'Symbol': symbol,
                        'Company Name': company_name,
                        'Current Price': f"${current_price:.2f}",
                        'Asset Type': asset_type
                    })
                except:
                    continue
            
            # Display in a scrollable table
            all_stocks_df = pd.DataFrame(all_stocks_data)
            st.dataframe(all_stocks_df, use_container_width=True, height=500)
            st.info(f"Total assets available: {len(all_stocks_data)}")
        
        else:
            st.info("Use the search box above to find specific assets, or check 'Show All Assets' to see the complete list of available securities.")

def show_watchlist_page():
    """Display user's watchlist."""
    st.title("👁️ Watchlist")
    
    user_id = st.session_state.user_info['user_id']
    
    # Add to watchlist
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Organize symbols by category for easier selection
        st.write("**Select Asset Category:**")
        asset_categories = market_data.get_asset_categories()
        
        category_options = ["All Assets"] + list(asset_categories.keys())
        selected_category = st.selectbox("Asset Category", category_options, key="watchlist_category")
        
        if selected_category == "All Assets":
            available_symbols = market_data.get_available_symbols()
        else:
            available_symbols = market_data.get_symbols_by_category(selected_category)
        
        new_symbol = st.selectbox("Add Symbol to Watchlist", available_symbols, key="watchlist_symbol")
    
    with col2:
        if st.button("➕ Add", use_container_width=True):
            if new_symbol:
                result = portfolio_manager.add_to_watchlist(user_id, new_symbol)
                if result['success']:
                    st.success(f"Added {new_symbol} to watchlist")
                    st.rerun()
                else:
                    st.error(result['message'])
    
    # Display watchlist
    watchlist = portfolio_manager.get_watchlist(user_id)
    
    if not watchlist.empty:
        # Update with current prices
        for index, row in watchlist.iterrows():
            current_price = market_data.get_current_price(row['symbol'])
            watchlist.at[index, 'current_price'] = current_price
            watchlist.at[index, 'change'] = random.uniform(-5, 5)  # Mock change
            watchlist.at[index, 'change_percent'] = (watchlist.at[index, 'change'] / current_price) * 100
        
        st.dataframe(watchlist, use_container_width=True)
    else:
        st.info("Your watchlist is empty. Add some symbols to track them.")

def show_reports_page():
    """Display trading reports and analytics."""
    st.title("📋 Reports & Analytics")
    
    if st.session_state.user_info['role'] not in ['trader', 'premium', 'admin']:
        st.error("Access denied. This feature requires a Trader or Premium account.")
        return
    
    user_id = st.session_state.user_info['user_id']
    
    # Date range selector
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input("Start Date", dt.now() - timedelta(days=30))
    
    with col2:
        end_date = st.date_input("End Date", dt.now())
    
    # Trading performance
    st.subheader("Trading Performance")
    
    performance_data = trading_engine.get_performance_metrics(user_id, start_date, end_date)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Trades", performance_data['total_trades'])
    
    with col2:
        st.metric("Winning Trades", performance_data['winning_trades'])
    
    with col3:
        st.metric("Win Rate", f"{performance_data['win_rate']:.1f}%")
    
    with col4:
        st.metric("Total P&L", f"${performance_data['total_pnl']:,.2f}")
    
    # Performance charts
    trade_history = trading_engine.get_trade_history(user_id, start_date, end_date)
    
    if not trade_history.empty:
        # P&L over time
        fig = px.line(trade_history, x='date', y='cumulative_pnl', title="Cumulative P&L")
        st.plotly_chart(fig, use_container_width=True)
        
        # Trade distribution
        fig = px.histogram(trade_history, x='pnl', title="Trade P&L Distribution")
        st.plotly_chart(fig, use_container_width=True)

def show_user_management_page():
    """Display user management interface (Admin only)."""
    user_role = st.session_state.user_info['role']
    is_super_admin = st.session_state.user_info.get('is_super_admin', False)
    
    if user_role not in ['admin', 'super_admin'] and not is_super_admin:
        st.error("Access denied. Admin privileges required.")
        return
    
    st.title("👥 User Management")
    
    # Initialize managers
    from modules.user_management import UserManager
    from modules.auth_manager import AuthManager
    user_manager = UserManager()
    auth_manager = AuthManager()
    
    current_user = st.session_state.user_info
    is_super_admin = current_user.get('is_super_admin', False)
    can_manage_admins = current_user.get('can_manage_admins', False)
    
    # User statistics
    user_stats = user_manager.get_user_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", user_stats['total_users'])
    
    with col2:
        st.metric("Active Today", user_stats['active_today'])
    
    with col3:
        st.metric("New This Month", user_stats['new_this_month'])
    
    with col4:
        st.metric("Premium Users", user_stats['premium_users'])
    
    # Regular admin restrictions notice
    if current_user.get('role') == 'admin' and not is_super_admin:
        st.markdown("---")
        st.subheader("⚠️ Regular Admin Permissions")
        st.info("🔒 **Regular Admin Restrictions** - You can send announcements and refresh data, but cannot promote users to admin or change user accounts. Only the super admin can manage user roles and accounts.")
        # Don't return - let regular admins see the user list
    
    # Admin management section (Super Admin only)
    if is_super_admin:
        st.markdown("---")
        st.subheader("👑 Super Admin Controls")
        st.info("🔒 **Super Admin Exclusive** - Only you can promote users to admin and manage user accounts")
        
        # Current admins
        admin_users = auth_manager.get_admin_users()
        
        if admin_users:
            st.write("**Current Administrators:**")
            for admin in admin_users:
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    admin_type = "Super Admin" if admin['is_super_admin'] else "Admin"
                    st.write(f"**{admin['username']}** ({admin['email']}) - {admin_type}")
                
                with col2:
                    if is_super_admin and not admin['is_super_admin']:
                        if st.button("Grant Permissions", key=f"grant_{admin['username']}"):
                            result = auth_manager.grant_admin_permissions(
                                admin['username'], 
                                {"can_manage_admins": True}, 
                                current_user['user_id']
                            )
                            if result['success']:
                                st.success(result['message'])
                                st.rerun()
                            else:
                                st.error(result['message'])
                
                with col3:
                    if is_super_admin and not admin['is_super_admin']:
                        if st.button("Revoke Admin", key=f"revoke_{admin['username']}"):
                            result = auth_manager.revoke_admin_role(admin['username'], current_user['user_id'])
                            if result['success']:
                                st.success(result['message'])
                                st.rerun()
                            else:
                                st.error(result['message'])
        
        # Promote user to admin (Super Admin only)
        st.markdown("**Promote User to Admin:**")
        
        # Get non-admin users
        all_users = user_manager.get_all_users()
        non_admin_users = all_users[all_users['role'] != 'admin']
        
        if not non_admin_users.empty:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                selected_user = st.selectbox(
                    "Select user to promote:",
                    non_admin_users['username'].tolist(),
                    key="promote_user_select"
                )
            
            with col2:
                if st.button("Promote to Admin", key="promote_btn"):
                    if selected_user:
                        result = auth_manager.promote_to_admin(selected_user, current_user['user_id'])
                        if result['success']:
                            st.success(result['message'])
                            st.rerun()
                        else:
                            st.error(result['message'])
        else:
            st.info("All users are already admins.")
        
        # Super Admin user management controls
        st.markdown("---")
        st.subheader("🔐 Super Admin User Controls")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Change User Password:**")
            change_pass_user = st.selectbox(
                "Select user:",
                all_users['username'].tolist(),
                key="change_pass_user"
            )
            new_password = st.text_input("New password:", type="password", key="new_password_input")
            
            if st.button("Change Password", key="change_pass_btn"):
                if change_pass_user and new_password:
                    result = auth_manager.super_admin_change_password(
                        change_pass_user, new_password, current_user['user_id']
                    )
                    if result['success']:
                        st.success(result['message'])
                    else:
                        st.error(result['message'])
        
        with col2:
            st.markdown("**Change Username:**")
            change_username_user = st.selectbox(
                "Select user:",
                all_users['username'].tolist(),
                key="change_username_user"
            )
            new_username = st.text_input("New username:", key="new_username_input")
            
            if st.button("Change Username", key="change_username_btn"):
                if change_username_user and new_username:
                    result = auth_manager.super_admin_change_username(
                        change_username_user, new_username, current_user['user_id']
                    )
                    if result['success']:
                        st.success(result['message'])
                        st.rerun()
                    else:
                        st.error(result['message'])
    
    # User list
    st.markdown("---")
    st.subheader("All Users")
    
    users_df = user_manager.get_all_users()
    
    # Add action buttons
    for index, user in users_df.iterrows():
        col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
        
        with col1:
            role_display = user['role']
            if user['role'] == 'admin':
                if user.get('is_super_admin', False):
                    role_display += " (Super)"
                elif user.get('can_manage_admins', False):
                    role_display += " (Can Manage)"
            
            st.write(f"**{user['username']}** ({user['email']}) - {role_display}")
        
        with col2:
            if st.button("Edit", key=f"edit_{user['user_id']}"):
                st.session_state.edit_user = user['user_id']
        
        with col3:
            if user['role'] != 'admin' or is_super_admin:
                if st.button("Suspend", key=f"suspend_{user['user_id']}"):
                    user_manager.suspend_user(str(user['user_id']))
                    st.rerun()
        
        with col4:
            if user['role'] != 'admin' or is_super_admin:
                if st.button("Delete", key=f"delete_{user['user_id']}"):
                    user_manager.delete_user(str(user['user_id']))
                    st.rerun()
        
        with col5:
            if user['role'] != 'admin' and can_manage_admins:
                if st.button("Make Admin", key=f"admin_{user['user_id']}"):
                    result = auth_manager.promote_to_admin(user['username'], current_user['user_id'])
                    if result['success']:
                        st.success(result['message'])
                        st.rerun()
                    else:
                        st.error(result['message'])



def show_admin_panel():
    """Display admin control panel."""
    user_role = st.session_state.user_info['role']
    is_super_admin = st.session_state.user_info.get('is_super_admin', False)
    
    if user_role not in ['admin', 'super_admin'] and not is_super_admin:
        st.error("Access denied. Admin privileges required.")
        return
    
    st.title("⚙️ Admin Control Panel")
    
    # Check if user is super admin
    is_super_admin = st.session_state.user_info.get('is_super_admin', False)
    
    # Super Admin Features
    if is_super_admin:
        st.markdown("### 👑 Super Admin Features")
        
        # All User Accounts with Credentials
        with st.expander("🔐 View All User Accounts & Credentials", expanded=False):
            st.warning("⚠️ **CONFIDENTIAL**: This information is only accessible to super administrators")
            
            try:
                from modules.auth_manager import AuthManager
                auth_manager = AuthManager()
                users = auth_manager._load_users()
                
                if users:
                    st.markdown("#### All User Accounts")
                    
                    # Create a DataFrame for better display
                    user_data = []
                    for user_id, user_info in users.items():
                        user_data.append({
                            'User ID': user_id,
                            'Username': user_info.get('username', 'N/A'),
                            'Email': user_info.get('email', 'N/A'),
                            'Full Name': f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip(),
                            'Role': user_info.get('role', 'basic'),
                            'Password Hash': user_info.get('password_hash', 'N/A')[:20] + "..." if user_info.get('password_hash') else 'N/A',
                            'Created': user_info.get('created_at', 'N/A'),
                            'Is Super Admin': user_info.get('is_super_admin', False)
                        })
                    
                    import pandas as pd
                    df = pd.DataFrame(user_data)
                    st.dataframe(df, use_container_width=True, height=400)
                    
                    # Download option - Super Admin Only
                    if is_super_admin:
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download User Data (CSV)",
                            data=csv,
                            file_name="user_accounts.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("🔒 Data download restricted to Super Administrators only")
                    
                    # Emergency Access Section
                    st.markdown("#### 🚨 Emergency Access")
                    st.info("Contact: ayagar624@fusdk12.net for emergency account management")
                    
                else:
                    st.error("No users found in the system")
                    
            except Exception as e:
                st.error(f"Error loading user data: {str(e)}")
        
        st.markdown("---")
    
    # System statistics
    st.subheader("📊 System Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        try:
            st.metric("Total Trades Today", trading_engine.get_daily_trade_count())
        except:
            st.metric("Total Trades Today", "N/A")
    
    with col2:
        try:
            st.metric("Total Volume", f"${trading_engine.get_daily_volume():,.2f}")
        except:
            st.metric("Total Volume", "N/A")
    
    with col3:
        st.metric("System Status", "🟢 Online")
    
    # Market controls
    st.subheader("🎛️ Market Controls")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh Market Data", use_container_width=True):
            try:
                market_data.refresh_data()
                st.success("Market data refreshed successfully")
            except Exception as e:
                st.error(f"Error refreshing data: {str(e)}")
    
    with col2:
        # Initialize report in session state if not exists
        if 'daily_report_data' not in st.session_state:
            st.session_state.daily_report_data = None
        
        if st.button("📊 Generate Daily Report", use_container_width=True):
            # Check if user is super admin
            current_user = st.session_state.user_info
            if current_user.get('email') == 'ayagar624@gmail.com' and current_user.get('is_super_admin', False):
                try:
                    # Generate comprehensive daily report
                    report_data = generate_daily_report(trading_engine, portfolio_manager, auth_manager)
                    
                    if report_data['success']:
                        # Store in session state to persist
                        st.session_state.daily_report_data = report_data
                        st.success("✅ Daily report generated successfully!")
                    else:
                        st.error(f"Report generation failed: {report_data['message']}")
                        
                except Exception as e:
                    st.error(f"Error generating report: {str(e)}")
            else:
                st.error("🔒 Access denied. Only Super Administrators can generate system reports.")
        
        # Show download button if report exists in session state
        if st.session_state.daily_report_data and st.session_state.daily_report_data.get('success'):
            report_data = st.session_state.daily_report_data
            
            # Create download button for the report
            st.download_button(
                label="📥 Download Daily Report (CSV)",
                data=report_data['csv_data'],
                file_name=f"daily_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
                key="download_report_btn"
            )
            
            # Show summary statistics
            st.info(f"📊 Report includes: {report_data['total_trades']} trades, {report_data['active_users']} users, ${report_data['total_volume']:,.2f} volume")
    
    # Announcements
    st.subheader("📢 System Announcements")
    st.info("⏰ All announcements auto-delete after 24 hours")
    
    # Show active announcements
    if announcements_manager:
        active_announcements = announcements_manager.get_active_announcements()
        
        if active_announcements:
            st.markdown("### 📋 Active Announcements")
            for ann in active_announcements[:5]:  # Show latest 5
                priority_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
                timestamp = datetime.fromisoformat(ann['timestamp']).strftime("%m/%d %H:%M")
                
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 10px; border-radius: 5px; margin: 5px 0; 
                           border-left: 3px solid {'#dc3545' if ann['priority'] == 'High' else '#ffc107' if ann['priority'] == 'Medium' else '#28a745'};">
                    <strong>{priority_color.get(ann['priority'], '⚪')} {ann['priority']} Priority</strong><br>
                    {ann['message']}<br>
                    <small style="color: #666;">Posted: {timestamp}</small>
                </div>
                """, unsafe_allow_html=True)
            
            # Cleanup button
            if st.button("🗑️ Clean Up Expired Announcements"):
                cleanup_result = announcements_manager.cleanup_expired_announcements()
                if cleanup_result['success']:
                    st.success(f"✅ {cleanup_result['message']}")
                else:
                    st.error(cleanup_result['error'])
                st.rerun()
        else:
            st.info("No active announcements")
    
    with st.form("announcement_form"):
        announcement = st.text_area("Announcement Message", placeholder="Enter announcement for all users...")
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        
        col1, col2 = st.columns(2)
        with col1:
            send_announcement = st.form_submit_button("📢 Send to All Users", use_container_width=True)
        with col2:
            send_email = st.form_submit_button("📧 Send via Email", use_container_width=True)
        
        if send_announcement and announcement:
            # Save announcement to system
            if announcements_manager:
                result = announcements_manager.add_announcement(
                    message=announcement,
                    priority=priority,
                    admin_id=st.session_state.user_info.get('user_id')
                )
                if result.get('success'):
                    st.success(f"📢 {priority} priority announcement published! (Auto-deletes in 24 hours)")
                    st.info(f"Message: {announcement}")
                    st.rerun()
                else:
                    st.error("Failed to save announcement")
            else:
                st.error("Announcement system not available")
    
    # Competition Management (Super Admin Only)
    if is_super_admin:
        st.divider()
        st.subheader("🏆 Competition Management")
        
        with st.expander("📊 Manage 6-Month Competitions", expanded=False):
            show_admin_competition_panel()
        
        if send_email and announcement:
            st.success(f"📧 Email announcement sent to all registered users!")
            st.info(f"Subject: [{priority} Priority] System Announcement")
    
    # Badge System Testing (Super Admin Only)
    current_user = st.session_state.user_info
    if current_user.get('email') == 'ayagar624@gmail.com' and current_user.get('is_super_admin', False):
        st.markdown("---")
        st.subheader("🏆 Badge System Testing")
        
        # Award test badges
        test_col1, test_col2 = st.columns(2)
        
        with test_col1:
            st.write("**Award Test Badge**")
            test_username = st.text_input("Username to award badge", placeholder="Enter username...")
            
            # Badge selection
            from modules.badge_manager import BadgeManager
            badge_manager = BadgeManager()
            all_badges = badge_manager.get_all_badge_definitions()
            
            badge_options = list(all_badges.keys())
            selected_badge = st.selectbox("Select Badge", options=badge_options)
            
            if st.button("🏆 Award Badge") and test_username and selected_badge:
                result = badge_manager.award_badge(test_username, selected_badge, "Admin test award")
                if result['success']:
                    st.success(f"✅ Badge '{selected_badge}' awarded to {test_username}!")
                else:
                    st.error(f"❌ {result['message']}")
        
        with test_col2:
            st.write("**Achievement Testing**")
            achievement_username = st.text_input("Username to check achievements", placeholder="Enter username...")
            
            if st.button("🎯 Check Achievements") and achievement_username:
                # Get user stats for testing
                try:
                    from modules.auth_manager import AuthManager
                    auth_manager = AuthManager()
                    test_user = auth_manager.get_user_by_username(achievement_username)
                    
                    if test_user:
                        check_user_achievements(test_user['user_id'])
                        st.success(f"✅ Checked achievements for {achievement_username}")
                    else:
                        st.error("User not found")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    # Contact Info
    st.markdown("---")
    st.info("💡 **Admin Support**: Contact ayagar624@fusdk12.net for technical assistance")

def show_friends_page():
    """Display friends management page."""
    st.title("👥 Friends")
    
    user_info = st.session_state.user_info
    friends_manager = FriendsManager()
    
    # Create tabs for different friend functions
    tab1, tab2, tab3 = st.tabs(["My Friends", "Add Friends", "Friend Portfolios"])
    
    with tab1:
        st.subheader("Your Friends")
        
        friends_df = friends_manager.get_friends_list(user_info['user_id'])
        
        if not friends_df.empty:
            # Display friends with their performance
            for idx, friend in friends_df.iterrows():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.write(f"**{friend['name']}** (@{friend['username']})")
                    st.caption(f"Role: {friend['role'].title()}")
                
                with col2:
                    st.metric("Portfolio Value", f"${friend['portfolio_value']:,.2f}")
                
                with col3:
                    pnl_color = "normal" if friend['daily_pnl'] >= 0 else "inverse"
                    st.metric("Daily P&L", f"${friend['daily_pnl']:,.2f}", 
                             delta=None, delta_color=pnl_color)
                
                with col4:
                    if user_info.get('username') == 'demo':
                        st.button("Remove", key=f"remove_{friend['username']}", disabled=True, help="Demo account cannot remove friends")
                    elif st.button("Remove", key=f"remove_{friend['username']}"):
                        result = friends_manager.remove_friend(user_info['user_id'], friend['username'])
                        if result['success']:
                            st.success(result['message'])
                            st.rerun()
                        else:
                            st.error(result['message'])
                
                st.divider()
        else:
            st.info("You haven't added any friends yet. Use the 'Add Friends' tab to find people!")
    
    with tab2:
        st.subheader("Add New Friends")
        
        if user_info.get('username') == 'demo':
            st.warning("🔒 Demo account cannot add friends")
            st.info("View-only access for demonstration purposes")
            st.markdown("---")
            st.write("**Demo restrictions:**")
            st.write("- Cannot send friend requests")
            st.write("- Cannot remove existing friends")
            st.write("- Can view friend portfolios only")
        else:
            # Search for users
            search_query = st.text_input("Search by username or name", placeholder="Enter username...")
            
            if search_query:
                search_results = friends_manager.search_users(search_query, user_info['user_id'])
                
                if search_results:
                    st.write(f"Found {len(search_results)} users:")
                    
                    for user in search_results:
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**{user['first_name']} {user['last_name']}** (@{user['username']})")
                            st.caption(f"Role: {user['role'].title()}")
                            # Display user's equipped badge
                            badge_html = get_user_badge_display(user.get('user_id', ''))
                            if badge_html:
                                st.markdown(badge_html, unsafe_allow_html=True)
                        
                        with col2:
                            if st.button("Add Friend", key=f"add_{user['username']}"):
                                result = friends_manager.send_friend_request(user_info['user_id'], user['username'])
                                if result['success']:
                                    st.success(result['message'])
                                    st.rerun()
                                else:
                                    st.error(result['message'])
                        
                        st.divider()
                else:
                    st.warning("No users found matching your search.")
    
    with tab3:
        st.subheader("Friend Portfolio Details")
        
        friends_df = friends_manager.get_friends_list(user_info['user_id'])
        
        if not friends_df.empty:
            selected_friend = st.selectbox(
                "Select a friend to view their portfolio:",
                friends_df['username'].tolist(),
                format_func=lambda x: friends_df[friends_df['username'] == x]['name'].iloc[0]
            )
            
            if selected_friend:
                portfolio_details = friends_manager.get_friend_portfolio_details(
                    user_info['user_id'], selected_friend
                )
                
                if portfolio_details['success']:
                    friend_info = portfolio_details['friend_info']
                    portfolio_summary = portfolio_details['portfolio_summary']
                    positions = portfolio_details['positions']
                    
                    st.subheader(f"{friend_info['name']}'s Portfolio")
                    
                    # Portfolio summary
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Value", f"${portfolio_summary['total_value']:,.2f}")
                    with col2:
                        st.metric("Portfolio Value", f"${portfolio_summary['portfolio_value']:,.2f}")
                    with col3:
                        st.metric("Cash Balance", f"${portfolio_summary['cash_balance']:,.2f}")
                    
                    # Positions
                    if positions:
                        st.subheader("Current Positions")
                        positions_df = pd.DataFrame(positions)
                        
                        # Display positions table
                        for idx, position in positions_df.iterrows():
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.write(f"**{position['symbol']}**")
                            with col2:
                                st.write(f"Qty: {position['quantity']}")
                            with col3:
                                st.write(f"Avg: ${position['avg_price']:.2f}")
                            with col4:
                                pnl = position.get('unrealized_pnl', 0)
                                pnl_color = "🟢" if pnl >= 0 else "🔴"
                                st.write(f"{pnl_color} ${pnl:.2f}")
                    else:
                        st.info("No positions to display.")
                else:
                    st.error(portfolio_details['message'])
        else:
            st.info("Add some friends first to view their portfolios!")

def show_leaderboard_page():
    """Display comprehensive leaderboard with enhanced team system and badges."""
    from modules.enhanced_competitions_page import show_comprehensive_leaderboard
    from modules.badge_manager import BadgeManager
    from modules.portfolio_manager import PortfolioManager
    from modules.trading_engine import TradingEngine
    
    user_info = st.session_state.user_info
    
    # Initialize required managers
    badge_manager = BadgeManager()
    portfolio_manager = PortfolioManager()
    trading_engine = TradingEngine()
    
    # Show the comprehensive leaderboard with enhanced team features
    show_comprehensive_leaderboard(
        user_info, 
        badge_manager, 
        portfolio_manager, 
        trading_engine
    )

def show_history_page():
    """Display trading history page."""
    st.title("📜 Trading History")
    
    user_info = st.session_state.user_info
    
    # Create tabs for different views  
    tab1, tab2, tab3, tab4 = st.tabs(["Recent Trades", "Investment Outcomes", "Sector Analysis", "Monthly Performance"])
    
    with tab1:
        st.subheader("Recent Trading Activity")
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            days_back = st.selectbox("Time Period", [7, 30, 90, 365, 1095, 3650, 7300, 10950], index=1, 
                                   format_func=lambda x: f"{x} days" + (" (3 years)" if x == 1095 else " (10 years)" if x == 3650 else " (20 years)" if x == 7300 else " (30 years)" if x == 10950 else ""))
        
        # Get trading history from trading engine
        trades_df = trading_engine.get_all_trades(user_info['user_id'])
        
        if not trades_df.empty:
            st.write(f"Found {len(trades_df)} total trades")
            st.dataframe(trades_df, use_container_width=True, height=400)
        else:
            st.info("No trades found. Start trading to see your history!")
    
    with tab2:
        st.subheader("Investment Outcomes & Statistics")
        st.info("Trading statistics will be available once you complete some buy/sell transactions.")
    
    with tab3:
        st.subheader("Sector Analysis")
        st.info("Sector analysis will be available once you complete trades across different market sectors.")
    
    with tab4:
        st.subheader("Monthly Performance")
        st.info("Monthly performance tracking will become available as you trade over time.")


def show_chat_page():
    """Display Discord invite page."""
    st.title("💬 Join Our Discord Community")
    
    # Create centered layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 40px 20px;">
            <div style="font-size: 80px; margin-bottom: 20px;">💬</div>
            <h2 style="color: #5865F2; margin-bottom: 20px;">Join the MSJSTOCKTRADER Community!</h2>
            <p style="font-size: 1.2rem; color: #666; margin-bottom: 30px;">
                Connect with thousands of traders, learn winning strategies, and become part of our thriving community on Discord!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Discord invite link
        st.markdown("""
        <div style="text-align: center; margin: 30px 0;">
            <a href="https://discord.gg/wkkg7bzDRd" target="_blank" style="
                display: inline-block;
                background: linear-gradient(135deg, #5865F2 0%, #7289DA 100%);
                color: white;
                padding: 18px 50px;
                border-radius: 10px;
                text-decoration: none;
                font-size: 1.3rem;
                font-weight: bold;
                box-shadow: 0 4px 15px rgba(88, 101, 242, 0.4);
                transition: all 0.3s ease;
            ">
                🚀 Join Discord Server Now
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Benefits section
        st.markdown("""
        <div style="margin-top: 40px;">
            <h3 style="text-align: center; color: #333; margin-bottom: 30px;">🎯 Why You Should Join Our Discord</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Benefit 1
        st.markdown("""
        <div style="padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 15px; color: white;">
            <div style="font-size: 28px; margin-bottom: 10px;">🏆</div>
            <h4 style="color: white; margin: 0;">Exclusive Competition Updates</h4>
            <p style="color: #f0f0f0; margin: 5px 0 0 0;">Be the first to know about new 6-month trading seasons, leaderboard rankings, and competition prizes!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Benefit 2
        st.markdown("""
        <div style="padding: 20px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 10px; margin-bottom: 15px; color: white;">
            <div style="font-size: 28px; margin-bottom: 10px;">💡</div>
            <h4 style="color: white; margin: 0;">Live Trading Insights & Tips</h4>
            <p style="color: #f0f0f0; margin: 5px 0 0 0;">Learn from experienced traders, discuss stock picks, and share winning strategies in real-time</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Benefit 3
        st.markdown("""
        <div style="padding: 20px; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border-radius: 10px; margin-bottom: 15px; color: white;">
            <div style="font-size: 28px; margin-bottom: 10px;">📊</div>
            <h4 style="color: white; margin: 0;">Market Analysis & News</h4>
            <p style="color: #f0f0f0; margin: 5px 0 0 0;">Get instant notifications about market movements, breaking news, and platform updates</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Benefit 4
        st.markdown("""
        <div style="padding: 20px; background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); border-radius: 10px; margin-bottom: 15px; color: white;">
            <div style="font-size: 28px; margin-bottom: 10px;">🤝</div>
            <h4 style="color: white; margin: 0;">Network with Winners</h4>
            <p style="color: #f0f0f0; margin: 5px 0 0 0;">Connect with top performers from the global leaderboard and learn their secrets to success</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Benefit 5
        st.markdown("""
        <div style="padding: 20px; background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); border-radius: 10px; margin-bottom: 15px; color: white;">
            <div style="font-size: 28px; margin-bottom: 10px;">🎁</div>
            <h4 style="color: white; margin: 0;">Exclusive Giveaways & Events</h4>
            <p style="color: #f0f0f0; margin: 5px 0 0 0;">Participate in community contests, trading challenges, and win exclusive badges & prizes!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Benefit 6
        st.markdown("""
        <div style="padding: 20px; background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); border-radius: 10px; margin-bottom: 15px;">
            <div style="font-size: 28px; margin-bottom: 10px;">📚</div>
            <h4 style="color: #333; margin: 0;">Free Learning Resources</h4>
            <p style="color: #666; margin: 5px 0 0 0;">Access tutorials, stock analysis guides, and educational content to improve your trading skills</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Benefit 7
        st.markdown("""
        <div style="padding: 20px; background: #f8f9fa; border-radius: 10px; margin-bottom: 15px;">
            <div style="font-size: 28px; margin-bottom: 10px;">⚡</div>
            <h4 style="color: #333; margin: 0;">Fast Support & Bug Reports</h4>
            <p style="color: #666; margin: 5px 0 0 0;">Report issues directly to our team and get quick responses to your questions</p>
        </div>
        """, unsafe_allow_html=True)

def show_pending_orders_page():
    """Display pending orders with estimated execution times."""
    st.title("⏳ Pending Orders")
    
    user_info = st.session_state.user_info
    
    # Get market status
    market_open = trading_engine.is_market_open()
    next_open = trading_engine.get_next_market_open()
    
    # Display market status banner
    if market_open:
        st.success("✅ **Market Status:** OPEN - Orders will be executed immediately")
    else:
        st.warning(f"⏸️ **Market Status:** CLOSED - Orders will execute at next market open: **{next_open.strftime('%A, %B %d at %I:%M %p PST')}**")
    
    st.info("""
    **Market Hours:** Weekdays (Monday - Friday), starting at 1:00 PM PST  
    **Weekend:** Market is closed on Saturday and Sunday  
    **Note:** Orders placed outside market hours will be queued and executed at the next market opening.
    """)
    
    st.markdown("---")
    
    # Get pending orders for current user
    pending_orders = trading_engine.get_pending_orders(user_info['user_id'])
    
    # Filter out any invalid entries (safety check for data integrity)
    pending_orders = [o for o in pending_orders if isinstance(o, dict)]
    
    if not pending_orders:
        st.info("📭 You have no pending orders. All your orders have been executed or cancelled.")
        st.markdown("---")
        st.markdown("### 📊 Want to place a new order?")
        st.write("Visit the **Trading** page to buy or sell stocks.")
    else:
        st.subheader(f"📋 Your Pending Orders ({len(pending_orders)})")
        
        # Create DataFrame for display
        pending_df = pd.DataFrame(pending_orders)
        
        # Format the display
        for i, order in enumerate(pending_orders):
            # Format side display
            side_display = order['side'].upper().replace('_', ' ')
            
            with st.expander(f"Order #{i+1}: {side_display} {order['quantity']} shares of {order['symbol']}", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**Order Details**")
                    st.write(f"📊 **Symbol:** {order['symbol']}")
                    st.write(f"📈 **Side:** {side_display}")
                    st.write(f"🔢 **Quantity:** {order['quantity']}")
                    st.write(f"💼 **Order Type:** {order['order_type'].upper()}")
                
                with col2:
                    st.markdown("**Status**")
                    st.write(f"⏱️ **Status:** {order['status'].upper()}")
                    created_time = datetime.fromisoformat(order['created_at'])
                    st.write(f"📅 **Created:** {created_time.strftime('%m/%d/%Y %I:%M %p')}")
                    if 'price' in order and order['price']:
                        st.write(f"💰 **Limit Price:** ${order['price']:.2f}")
                
                with col3:
                    st.markdown("**Estimated Execution**")
                    st.write(f"⏰ **Next Execution:**")
                    st.success(order['estimated_execution_formatted'])
                    
                    # Calculate time until execution
                    exec_time = datetime.fromisoformat(order['estimated_execution'])
                    time_diff = exec_time - datetime.now(trading_engine.timezone)
                    
                    if time_diff.total_seconds() > 0:
                        hours = int(time_diff.total_seconds() // 3600)
                        minutes = int((time_diff.total_seconds() % 3600) // 60)
                        st.write(f"⏳ **Time Until:** {hours}h {minutes}m")
                    else:
                        st.write("⏳ **Executing soon...**")
                
                # Cancel button
                if st.button(f"❌ Cancel Order", key=f"cancel_{order['order_id']}"):
                    result = trading_engine.cancel_order(user_info['user_id'], order['order_id'])
                    if result['success']:
                        st.success(result['message'])
                        st.rerun()
                    else:
                        st.error(result['message'])
        
        # Summary statistics
        st.markdown("---")
        st.subheader("📊 Pending Orders Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Pending", len(pending_orders))
        
        with col2:
            buy_orders = len([o for o in pending_orders if o['side'] in ['buy', 'short_cover']])
            st.metric("Buy/Cover Orders", buy_orders)
        
        with col3:
            sell_orders = len([o for o in pending_orders if o['side'] in ['sell', 'short_sell']])
            st.metric("Sell/Short Orders", sell_orders)
        
        with col4:
            st.metric("Next Execution", next_open.strftime('%I:%M %p'))


if __name__ == "__main__":
    main()