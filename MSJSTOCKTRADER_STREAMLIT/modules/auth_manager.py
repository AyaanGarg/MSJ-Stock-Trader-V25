import streamlit as st
import bcrypt
import json
import os
import secrets
import string
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import uuid
from modules.email_service import EmailService

class AuthManager:
    """Handles user authentication and session management."""
    
    def __init__(self):
        self.users_file = "data/users.json"
        self.sessions_file = "data/sessions.json"
        self.reset_codes_file = "data/reset_codes.json"
        self.email_service = EmailService()
        self._ensure_data_directory()
        self._initialize_users()
    
    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist."""
        os.makedirs("data", exist_ok=True)
    
    def _initialize_users(self):
        """Initialize users file with demo account and super admin if it doesn't exist."""
        if not os.path.exists(self.users_file):
            default_users = {
                "ayaan_garg": {
                    "user_id": str(uuid.uuid4()),
                    "username": "Ayaan Garg",
                    "email": "ayagar624@gmail.com",
                    "password_hash": bcrypt.hashpw("78muydwnEY+-i8Y".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    "first_name": "Ayaan",
                    "last_name": "Garg",
                    "role": "super_admin",
                    "account_type": "Corporate",
                    "phone": "+1-555-0000",
                    "created_at": datetime.now().isoformat(),
                    "last_login": None,
                    "is_active": True,
                    "failed_login_attempts": 0,
                    "is_super_admin": True,
                    "can_manage_admins": True,
                    "friends": []
                },
                "demo": {
                    "user_id": str(uuid.uuid4()),
                    "username": "demo",
                    "email": "demo@stocktrade.pro",
                    "password_hash": bcrypt.hashpw("demo123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    "first_name": "Demo",
                    "last_name": "User",
                    "role": "trader",
                    "account_type": "Individual",
                    "phone": "+1-555-0001",
                    "created_at": datetime.now().isoformat(),
                    "last_login": None,
                    "is_active": True,
                    "failed_login_attempts": 0,
                    "is_super_admin": False,
                    "can_manage_admins": False,
                    "friends": []
                }
            }
            
            self._save_users(default_users)
    
    def _load_users(self) -> Dict:
        """Load users from file."""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_users(self, users: Dict):
        """Save users to file."""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    def authenticate_user(self, email: str, password: str) -> Dict:
        """Authenticate user with email and password."""
        users = self._load_users()
        
        # Find user by email
        found_user = None
        found_username = None
        
        for username, user_data in users.items():
            if user_data.get("email", "").lower() == email.lower():
                found_user = user_data
                found_username = username
                break
        
        if not found_user:
            return {"success": False, "message": "Invalid email or password"}
        
        # Check if account is active
        if not found_user.get("is_active", True):
            return {"success": False, "message": "Account is suspended"}
        
        # Check password
        if bcrypt.checkpw(password.encode('utf-8'), found_user["password_hash"].encode('utf-8')):
            # Reset failed login attempts on successful login
            found_user["failed_login_attempts"] = 0
            found_user["last_login"] = datetime.now().isoformat()
            
            # Update user data
            users[found_username] = found_user
            self._save_users(users)
            
            return {
                "success": True,
                "user_info": found_user,
                "message": "Login successful"
            }
        else:
            # Increment failed login attempts (tracking only, no suspension)
            found_user["failed_login_attempts"] = found_user.get("failed_login_attempts", 0) + 1
            
            users[found_username] = found_user
            self._save_users(users)
            
            return {"success": False, "message": "Invalid email or password"}
    
    def register_user(self, email: str, password: str, first_name: str, last_name: str, phone: str = "", account_type: str = "Individual") -> Dict:
        """Register a new user with simplified parameters."""
        user_data = {
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "account_type": account_type
        }
        return self.register_user_dict(user_data)
    
    def register_user_dict(self, user_data: Dict) -> Dict:
        """Register a new user."""
        users = self._load_users()
        
        # Check if username already exists
        if user_data["username"] in users:
            return {"success": False, "message": "Username already exists"}
        
        # Check if email already exists
        for existing_user in users.values():
            if existing_user["email"] == user_data["email"]:
                return {"success": False, "message": "Email already registered"}
        
        # Hash password
        password_hash = bcrypt.hashpw(user_data["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create new user
        new_user = {
            "user_id": str(uuid.uuid4()),
            "username": user_data["username"],
            "email": user_data["email"],
            "password_hash": password_hash,
            "first_name": user_data["first_name"],
            "last_name": user_data["last_name"],
            "role": "trader",  # Default role for new registrations
            "account_type": user_data.get("account_type", "Individual"),
            "phone": user_data.get("phone", ""),
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "is_active": True,
            "failed_login_attempts": 0,
            "is_super_admin": False,
            "can_manage_admins": False
        }
        
        # Save user
        users[user_data["username"]] = new_user
        self._save_users(users)
        
        # Create initial portfolio
        from modules.portfolio_manager import PortfolioManager
        portfolio_manager = PortfolioManager()
        portfolio_manager.create_portfolio(new_user["user_id"])
        
        return {"success": True, "message": "User registered successfully", "user_id": new_user["user_id"]}
    
    def _load_reset_codes(self) -> Dict:
        """Load password reset codes from file."""
        try:
            with open(self.reset_codes_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _save_reset_codes(self, codes: Dict):
        """Save password reset codes to file."""
        with open(self.reset_codes_file, 'w') as f:
            json.dump(codes, f, indent=2)
    
    def _generate_reset_code(self) -> str:
        """Generate a secure 6-digit reset code."""
        return ''.join(secrets.choice(string.digits) for _ in range(6))
    
    def send_password_reset(self, email: str) -> Dict:
        """Send password reset code via email with improved timing and reliability."""
        users = self._load_users()
        
        # Find user by email (case insensitive)
        user_data = None
        for user in users.values():
            if user.get('email', '').lower() == email.lower():
                user_data = user
                break
        
        if not user_data:
            return {
                "success": False,
                "message": "No account found with this email address."
            }
        
        # Generate reset code
        reset_code = self._generate_reset_code()
        
        # Store reset code with longer expiration (30 minutes for better UX)
        reset_codes = self._load_reset_codes()
        reset_codes[email.lower()] = {
            "code": reset_code,
            "expires_at": (datetime.now() + timedelta(minutes=30)).isoformat(),
            "user_id": user_data['user_id'],
            "created_at": datetime.now().isoformat()
        }
        self._save_reset_codes(reset_codes)
        
        # Try to send email with enhanced error handling
        username = user_data.get('first_name', user_data.get('username', 'User'))
        
        # Try to send email first
        try:
            email_sent = self.email_service.send_password_reset_email(email, reset_code, username)
            
            if email_sent:
                return {
                    "success": True,
                    "message": f"Password reset code sent to {email}. Check your email and enter the code below.",
                    "reset_code": reset_code,  # Still show code as backup
                    "email_sent": True,
                    "expires_in": "30 minutes",
                    "fallback_mode": False,
                    "instant_mode": False
                }
            else:
                # Email failed, use instant mode as fallback
                return {
                    "success": True,
                    "message": "Email service unavailable. Your reset code is displayed below for immediate use.",
                    "reset_code": reset_code,
                    "email_sent": False,
                    "expires_in": "30 minutes",
                    "fallback_mode": True,
                    "instant_mode": True
                }
        except Exception as e:
            # Error sending email, use instant mode as fallback
            print(f"Error sending password reset email: {e}")
            return {
                "success": True,
                "message": f"Email error occurred: {str(e)}. Your reset code is displayed below for immediate use.",
                "reset_code": reset_code,
                "email_sent": False,
                "expires_in": "30 minutes",
                "fallback_mode": True,
                "instant_mode": True,
                "error_details": str(e)
            }
    
    def verify_reset_code(self, email: str, code: str) -> Dict:
        """Verify password reset code with improved timing."""
        reset_codes = self._load_reset_codes()
        email_key = email.lower()
        
        if email_key not in reset_codes:
            return {
                "success": False,
                "message": "No reset code found for this email. Please request a new code."
            }
        
        stored_data = reset_codes[email_key]
        
        # Check if code has expired (30 minutes)
        expires_at = datetime.fromisoformat(stored_data['expires_at'])
        if datetime.now() > expires_at:
            # Remove expired code
            del reset_codes[email_key]
            self._save_reset_codes(reset_codes)
            return {
                "success": False,
                "message": "Reset code has expired (30 minutes). Please request a new one."
            }
        
        # Check if code matches
        if stored_data['code'] != code:
            return {
                "success": False,
                "message": "Invalid reset code."
            }
        
        return {
            "success": True,
            "message": "Reset code verified successfully.",
            "user_id": stored_data['user_id']
        }
    
    def reset_password_with_code(self, email: str, code: str, new_password: str) -> Dict:
        """Reset password using verified code."""
        # First verify the code
        verification = self.verify_reset_code(email, code)
        if not verification["success"]:
            return verification
        
        user_id = verification["user_id"]
        
        # Update password
        users = self._load_users()
        user_updated = False
        
        for user_key, user_data in users.items():
            if user_data['user_id'] == user_id:
                # Hash new password
                hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                user_data['password_hash'] = hashed_password.decode('utf-8')
                user_data['failed_login_attempts'] = 0  # Reset failed attempts
                user_updated = True
                break
        
        if user_updated:
            self._save_users(users)
            
            # Remove used reset code
            reset_codes = self._load_reset_codes()
            email_key = email.lower()
            if email_key in reset_codes:
                del reset_codes[email_key]
                self._save_reset_codes(reset_codes)
            
            return {
                "success": True,
                "message": "Password has been reset successfully."
            }
        else:
            return {
                "success": False,
                "message": "Failed to update password."
            }
    
    def get_demo_account(self) -> Dict:
        """Get demo account for quick access."""
        users = self._load_users()
        
        if "demo" in users:
            demo_user = users["demo"]
            # Update last login
            demo_user["last_login"] = datetime.now().isoformat()
            users["demo"] = demo_user
            self._save_users(users)
            
            return demo_user
        else:
            # Create demo account if it doesn't exist
            demo_user = {
                "user_id": str(uuid.uuid4()),
                "username": "demo",
                "email": "demo@stocktrade.pro",
                "password_hash": bcrypt.hashpw("demo123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                "first_name": "Demo",
                "last_name": "User",
                "role": "trader",
                "account_type": "Individual",
                "phone": "+1-555-0001",
                "created_at": datetime.now().isoformat(),
                "last_login": datetime.now().isoformat(),
                "is_active": True,
                "failed_login_attempts": 0,
                "is_super_admin": False,
                "can_manage_admins": False
            }
            
            users["demo"] = demo_user
            self._save_users(users)
            
            return demo_user
    
    def change_password(self, username: str, old_password: str, new_password: str) -> Dict:
        """Change user password."""
        users = self._load_users()
        
        if username not in users:
            return {"success": False, "message": "User not found"}
        
        user = users[username]
        
        # Verify old password
        if not bcrypt.checkpw(old_password.encode('utf-8'), user["password_hash"].encode('utf-8')):
            return {"success": False, "message": "Current password is incorrect"}
        
        # Hash new password
        new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Update password
        user["password_hash"] = new_password_hash
        users[username] = user
        self._save_users(users)
        
        return {"success": True, "message": "Password changed successfully"}
    
    def _send_welcome_email(self, email: str, first_name: str, last_name: str, username: str):
        """Send welcome email for new account creation."""
        try:
            from modules.email_service import EmailService
            
            email_service = EmailService()
            user_name = f"{first_name} {last_name}".strip()
            if not user_name:
                user_name = username
            
            result = email_service.send_welcome_email(email, user_name, username)
            
            if not result['success']:
                print(f"Failed to send welcome email: {result['message']}")
        except Exception as e:
            print(f"Welcome email service error: {str(e)}")
    
    def update_user_role(self, username: str, new_role: str, admin_user_id: str = None) -> Dict:
        """Update user role (admin only)."""
        users = self._load_users()
        
        if username not in users:
            return {"success": False, "message": "User not found"}
        
        valid_roles = ["basic", "trader", "premium", "admin"]
        if new_role not in valid_roles:
            return {"success": False, "message": f"Invalid role. Must be one of: {valid_roles}"}
        
        # Check if promoting to admin and verify permissions
        if new_role == "admin" and admin_user_id:
            admin_user = self.get_user_by_id(admin_user_id)
            if not admin_user or not admin_user.get("can_manage_admins", False):
                return {"success": False, "message": "Insufficient permissions to promote users to admin"}
        
        old_role = users[username]["role"]
        users[username]["role"] = new_role
        
        # If promoting to admin, give basic admin permissions but not super admin
        if new_role == "admin":
            users[username]["is_super_admin"] = False
            users[username]["can_manage_admins"] = False
        elif old_role == "admin":
            # If demoting from admin, remove admin flags
            users[username]["is_super_admin"] = False
            users[username]["can_manage_admins"] = False
        
        self._save_users(users)
        
        return {"success": True, "message": f"User role updated from {old_role} to {new_role}"}
    
    def update_username(self, user_id: str, new_username: str) -> Dict:
        """Update user's username (user can change their own username)."""
        users = self._load_users()
        
        # Check if new username already exists
        for existing_username, user_data in users.items():
            if existing_username.lower() == new_username.lower() and user_data["user_id"] != user_id:
                return {"success": False, "message": "Username already exists"}
        
        # Find user by ID and update username
        found_user = None
        old_username = None
        
        for username, user_data in users.items():
            if user_data.get("user_id") == user_id:
                found_user = user_data
                old_username = username
                break
        
        if not found_user:
            return {"success": False, "message": "User not found"}
        
        # Update username in dictionary
        found_user["username"] = new_username
        users[new_username] = found_user
        
        # Remove old username key if different
        if old_username != new_username:
            del users[old_username]
        
        self._save_users(users)
        
        return {"success": True, "message": f"Username updated to {new_username}"}
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by user ID."""
        users = self._load_users()
        
        for user in users.values():
            if user["user_id"] == user_id:
                return user
        
        return None
    
    def promote_to_admin(self, target_username: str, admin_user_id: str) -> Dict:
        """Promote a user to admin role (super admin only)."""
        users = self._load_users()
        
        # Verify super admin permissions - ONLY super admins can promote users to admin
        admin_user = self.get_user_by_id(admin_user_id)
        if not admin_user or not admin_user.get("is_super_admin", False):
            return {"success": False, "message": "Only super admins can promote users to admin role"}
        
        if target_username not in users:
            return {"success": False, "message": "User not found"}
        
        target_user = users[target_username]
        if target_user["role"] == "admin":
            return {"success": False, "message": "User is already an admin"}
        
        # Promote to admin
        target_user["role"] = "admin"
        target_user["is_super_admin"] = False
        target_user["can_manage_admins"] = False
        target_user["promoted_to_admin_at"] = datetime.now().isoformat()
        target_user["promoted_by"] = admin_user_id
        
        users[target_username] = target_user
        self._save_users(users)
        
        return {"success": True, "message": f"User {target_username} promoted to admin successfully"}
    
    def grant_admin_permissions(self, target_username: str, permissions: Dict, admin_user_id: str) -> Dict:
        """Grant specific admin permissions (super admin only)."""
        users = self._load_users()
        
        # Verify super admin permissions
        admin_user = self.get_user_by_id(admin_user_id)
        if not admin_user or not admin_user.get("is_super_admin", False):
            return {"success": False, "message": "Only super admins can grant admin permissions"}
        
        if target_username not in users:
            return {"success": False, "message": "User not found"}
        
        target_user = users[target_username]
        if target_user["role"] != "admin":
            return {"success": False, "message": "User must be an admin to receive admin permissions"}
        
        # Grant permissions
        if permissions.get("can_manage_admins"):
            target_user["can_manage_admins"] = True
        
        target_user["permissions_updated_at"] = datetime.now().isoformat()
        target_user["permissions_updated_by"] = admin_user_id
        
        users[target_username] = target_user
        self._save_users(users)
        
        return {"success": True, "message": f"Admin permissions updated for {target_username}"}
    
    def revoke_admin_role(self, target_username: str, admin_user_id: str) -> Dict:
        """Revoke admin role from a user (super admin only)."""
        users = self._load_users()
        
        # Verify super admin permissions
        admin_user = self.get_user_by_id(admin_user_id)
        if not admin_user or not admin_user.get("is_super_admin", False):
            return {"success": False, "message": "Only super admins can revoke admin roles"}
        
        if target_username not in users:
            return {"success": False, "message": "User not found"}
        
        target_user = users[target_username]
        if target_user["role"] != "admin":
            return {"success": False, "message": "User is not an admin"}
        
        # Prevent super admin from revoking their own role
        if target_user.get("is_super_admin", False):
            return {"success": False, "message": "Cannot revoke super admin role"}
        
        # Revoke admin role
        target_user["role"] = "trader"  # Demote to trader
        target_user["is_super_admin"] = False
        target_user["can_manage_admins"] = False
        target_user["admin_revoked_at"] = datetime.now().isoformat()
        target_user["admin_revoked_by"] = admin_user_id
        
        users[target_username] = target_user
        self._save_users(users)
        
        return {"success": True, "message": f"Admin role revoked from {target_username}"}
    
    def get_admin_users(self) -> List[Dict]:
        """Get all admin users."""
        users = self._load_users()
        
        admin_users = []
        for username, user_data in users.items():
            if user_data.get("role") == "admin":
                admin_users.append({
                    "username": username,
                    "email": user_data.get("email"),
                    "first_name": user_data.get("first_name"),
                    "last_name": user_data.get("last_name"),
                    "is_super_admin": user_data.get("is_super_admin", False),
                    "can_manage_admins": user_data.get("can_manage_admins", False),
                    "created_at": user_data.get("created_at"),
                    "last_login": user_data.get("last_login")
                })
        
        return admin_users
    
    def super_admin_change_password(self, target_username: str, new_password: str, admin_user_id: str) -> Dict:
        """Super admin function to change any user's password."""
        users = self._load_users()
        
        # Verify super admin permissions
        admin_user = self.get_user_by_id(admin_user_id)
        if not admin_user or not admin_user.get("is_super_admin", False):
            return {"success": False, "message": "Only super admins can change other users' passwords"}
        
        if target_username not in users:
            return {"success": False, "message": "User not found"}
        
        # Hash new password
        new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Update user password
        users[target_username]["password_hash"] = new_password_hash
        users[target_username]["password_changed_by_admin"] = admin_user_id
        users[target_username]["password_changed_at"] = datetime.now().isoformat()
        
        self._save_users(users)
        
        return {"success": True, "message": f"Password changed successfully for user {target_username}"}
    
    def super_admin_change_username(self, old_username: str, new_username: str, admin_user_id: str) -> Dict:
        """Super admin function to change any user's username."""
        users = self._load_users()
        
        # Verify super admin permissions
        admin_user = self.get_user_by_id(admin_user_id)
        if not admin_user or not admin_user.get("is_super_admin", False):
            return {"success": False, "message": "Only super admins can change other users' usernames"}
        
        if old_username not in users:
            return {"success": False, "message": "User not found"}
        
        if new_username in users and new_username != old_username:
            return {"success": False, "message": "Username already exists"}
        
        # Update username
        user_data = users[old_username]
        user_data["username"] = new_username
        user_data["username_changed_by_admin"] = admin_user_id
        user_data["username_changed_at"] = datetime.now().isoformat()
        
        # Add user with new username and remove old
        users[new_username] = user_data
        if old_username != new_username:
            del users[old_username]
        
        self._save_users(users)
        
        return {"success": True, "message": f"Username changed from {old_username} to {new_username}"}
    
    def validate_session(self, session_token: str) -> Optional[Dict]:
        """Validate session token."""
        # In a real application, you would validate session tokens
        # For demo purposes, we'll assume all sessions are valid
        # This would typically check against a sessions database
        return {"valid": True}