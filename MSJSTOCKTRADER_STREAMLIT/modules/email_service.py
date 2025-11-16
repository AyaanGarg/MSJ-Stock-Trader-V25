"""
Email Service for MSJSTOCKTRADER
Handles sending emails for notifications, team invitations, and account creation.
Supports both Replit Gmail connector (OAuth2) and standard SMTP for Streamlit deployment.
"""

import os
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
from datetime import datetime

class EmailService:
    """Handles email notifications using Gmail SMTP or Gmail API depending on environment."""
    
    def __init__(self):
        self.email = os.environ.get('GMAIL_EMAIL')
        self.app_password = os.environ.get('GMAIL_APP_PASSWORD')
        
        # For Replit Gmail connector (OAuth2)
        self.client_id = os.environ.get('GMAIL_CLIENT_ID')
        self.client_secret = os.environ.get('GMAIL_CLIENT_SECRET')
        self.refresh_token = os.environ.get('GMAIL_REFRESH_TOKEN')
        
        # SMTP settings
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
    def _send_email_smtp(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> Dict:
        """Send email using Gmail SMTP (for Streamlit Community Cloud deployment)."""
        try:
            if not self.email or not self.app_password:
                return {"success": False, "message": "Email credentials not configured"}
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text content if provided
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Add HTML content
            if html_content:
                html_part = MIMEText(html_content, 'html')
                msg.attach(html_part)
            
            # Send email via SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.app_password)
                server.send_message(msg)
            
            return {"success": True, "message": "Email sent successfully"}
            
        except Exception as e:
            return {"success": False, "message": f"Failed to send email: {str(e)}"}
    
    def _send_email_oauth2(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> Dict:
        """Send email using Gmail API with OAuth2 (for Replit deployment)."""
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            from googleapiclient.errors import HttpError
            
            if not all([self.client_id, self.client_secret, self.refresh_token]):
                return {"success": False, "message": "OAuth2 credentials not configured"}
            
            # Create Gmail API service
            creds = Credentials(
                None,
                refresh_token=self.refresh_token,
                client_id=self.client_id,
                client_secret=self.client_secret,
                token_uri="https://oauth2.googleapis.com/token",
                scopes=["https://www.googleapis.com/auth/gmail.send"]
            )
            
            service = build("gmail", "v1", credentials=creds)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            if html_content:
                html_part = MIMEText(html_content, 'html')
                msg.attach(html_part)
            
            # Encode and send
            raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            sent_message = service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return {"success": True, "message": f"Email sent successfully (ID: {sent_message['id']})"}
            
        except ImportError:
            return {"success": False, "message": "Gmail API libraries not available"}
        except Exception as e:
            return {"success": False, "message": f"OAuth2 email failed: {str(e)}"}
        
    def _send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> Dict:
        """Send email using available method (OAuth2 for Replit, SMTP for Streamlit)."""
        # Try OAuth2 first (Replit connector)
        if all([self.client_id, self.client_secret, self.refresh_token]):
            result = self._send_email_oauth2(to_email, subject, html_content, text_content)
            if result['success']:
                return result
        
        # Fall back to SMTP (Streamlit Community Cloud)
        if self.email and self.app_password:
            return self._send_email_smtp(to_email, subject, html_content, text_content)
        
        return {"success": False, "message": "No email credentials configured"}
    
    def send_email(self, to_email: str, subject: str, html_content: str = None, text_content: str = None) -> Dict:
        """Public method to send email."""
        if not html_content and not text_content:
            return {"success": False, "message": "Either html_content or text_content must be provided"}
        
        return self._send_email(to_email, subject, html_content or "", text_content)
    
    def send_team_invitation_email(self, invitee_email: str, invitee_name: str, team_name: str, 
                                 inviter_name: str, invitation_id: str) -> Dict:
        """Send team invitation email."""
        subject = f"Team Invitation: Join '{team_name}' on MSJSTOCKTRADER"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; color: #2196F3; margin-bottom: 30px; }}
                .team-info {{ background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .action-button {{ display: inline-block; background: #2196F3; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 5px; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤝 Team Invitation</h1>
                    <h2>MSJSTOCKTRADER</h2>
                </div>
                
                <p>Hi {invitee_name},</p>
                
                <p>You've been invited to join a team on MSJSTOCKTRADER!</p>
                
                <div class="team-info">
                    <h3>Team: {team_name}</h3>
                    <p><strong>Invited by:</strong> {inviter_name}</p>
                    <p><strong>Platform:</strong> MSJSTOCKTRADER</p>
                    <p><strong>Message:</strong> {inviter_name} wants you to join their trading team and compete together!</p>
                </div>
                
                <p>To accept or decline this invitation:</p>
                <ol>
                    <li>Log in to your MSJSTOCKTRADER account</li>
                    <li>Go to the "Leaderboard" section</li>
                    <li>Click on the "Team Invitations" tab</li>
                    <li>Find your invitation and respond</li>
                </ol>
                
                <p><strong>Note:</strong> This invitation will expire in 7 days.</p>
                
                <div class="footer">
                    <p>This email was sent from MSJSTOCKTRADER - Real Market Data Trading Platform</p>
                    <p>If you didn't expect this invitation, you can safely ignore this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Team Invitation - MSJSTOCKTRADER
        
        Hi {invitee_name},
        
        You've been invited to join team '{team_name}' by {inviter_name} on MSJSTOCKTRADER!
        
        To respond to this invitation:
        1. Log in to your MSJSTOCKTRADER account
        2. Go to Leaderboard > Team Invitations
        3. Accept or decline the invitation
        
        This invitation expires in 7 days.
        
        Thanks,
        MSJSTOCKTRADER Team
        """
        
        return self._send_email(invitee_email, subject, html_content, text_content)
    
    def send_welcome_email(self, user_email: str, user_name: str, username: str) -> Dict:
        """Send welcome email for new account creation."""
        subject = "Welcome to MSJSTOCKTRADER - Your Account is Ready!"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; color: #2196F3; margin-bottom: 30px; }}
                .welcome-info {{ background: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .features {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Welcome to MSJSTOCKTRADER!</h1>
                    <h2>Your Account is Ready</h2>
                </div>
                
                <p>Hi {user_name},</p>
                
                <p>Welcome to MSJSTOCKTRADER! Your account has been successfully created and you're ready to start your trading journey.</p>
                
                <div class="welcome-info">
                    <h3>✅ Account Details</h3>
                    <p><strong>Username:</strong> {username}</p>
                    <p><strong>Email:</strong> {user_email}</p>
                    <p><strong>Starting Balance:</strong> $100,000 (virtual money)</p>
                    <p><strong>Account Type:</strong> Trader</p>
                </div>
                
                <div class="features">
                    <h3>🚀 What You Can Do:</h3>
                    <ul>
                        <li><strong>📈 Trade Real Stocks:</strong> Buy and sell 400+ real US stocks with live market data</li>
                        <li><strong>🏆 Compete & Badges:</strong> Earn badges and compete on leaderboards</li>
                        <li><strong>🤝 Team Trading:</strong> Create or join teams for collaborative trading</li>
                        <li><strong>👥 Social Features:</strong> Add friends and share portfolio performance</li>
                        <li><strong>💬 Chat System:</strong> Connect with other traders in real-time</li>
                        <li><strong>📊 Advanced Analytics:</strong> Track your performance with detailed charts</li>
                    </ul>
                </div>
                
                <p><strong>Getting Started:</strong></p>
                <ol>
                    <li>Log in to your account</li>
                    <li>Explore the Market Data section to see available stocks</li>
                    <li>Start trading with your $100,000 virtual balance</li>
                    <li>Add friends and join the community</li>
                </ol>
                
                <div class="footer">
                    <p>Happy Trading!</p>
                    <p>The MSJSTOCKTRADER Team</p>
                    <p>Real Market Data • Safe Virtual Trading • Social Competition</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to MSJSTOCKTRADER!
        
        Hi {user_name},
        
        Your account has been successfully created!
        
        Account Details:
        - Username: {username}
        - Email: {user_email}
        - Starting Balance: $100,000 (virtual)
        
        Features Available:
        - Trade 400+ real US stocks with live data
        - Compete on leaderboards and earn badges
        - Create/join teams for collaborative trading
        - Social features and chat system
        - Advanced portfolio analytics
        
        Start trading today with your virtual $100,000!
        
        Happy Trading,
        MSJSTOCKTRADER Team
        """
        
        return self._send_email(user_email, subject, html_content, text_content)
    
    def send_team_notification_email(self, user_email: str, user_name: str, 
                                   notification_title: str, notification_message: str) -> Dict:
        """Send general team notification email."""
        subject = f"Team Notification: {notification_title}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; color: #FF9800; margin-bottom: 30px; }}
                .notification {{ background: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #FF9800; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔔 Team Notification</h1>
                    <h2>MSJSTOCKTRADER</h2>
                </div>
                
                <p>Hi {user_name},</p>
                
                <div class="notification">
                    <h3>{notification_title}</h3>
                    <p>{notification_message}</p>
                </div>
                
                <p>Log in to your MSJSTOCKTRADER account to see more details and take any necessary actions.</p>
                
                <div class="footer">
                    <p>This notification was sent from MSJSTOCKTRADER</p>
                    <p>Team trading • Real market data • Social competition</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Team Notification - MSJSTOCKTRADER
        
        Hi {user_name},
        
        {notification_title}
        
        {notification_message}
        
        Log in to your account for more details.
        
        Thanks,
        MSJSTOCKTRADER Team
        """
        
        return self._send_email(user_email, subject, html_content, text_content)