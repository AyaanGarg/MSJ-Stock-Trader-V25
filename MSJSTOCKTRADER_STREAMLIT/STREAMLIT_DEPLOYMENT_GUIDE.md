# MSJSTOCKTRADER - Streamlit Community Cloud Deployment Guide

## 📦 Quick Start

This package contains everything you need to deploy MSJSTOCKTRADER on Streamlit Community Cloud via GitHub.

## 🚀 Deployment Steps

### Step 1: Upload to GitHub

1. **Create a new GitHub repository**
   - Go to https://github.com/new
   - Name it: `msjstocktrader` (or any name you prefer)
   - Set to **Public** (required for Streamlit Community Cloud free tier)
   - Click "Create repository"

2. **Upload the files**
   - Extract this package to a folder on your computer
   - Upload all files to your GitHub repository using one of these methods:
     - **Via GitHub web interface**: Click "Add file" > "Upload files"
     - **Via Git command line**:
       ```bash
       git clone https://github.com/YOUR_USERNAME/msjstocktrader.git
       cd msjstocktrader
       # Copy all extracted files here
       git add .
       git commit -m "Initial deployment"
       git push
       ```

### Step 2: Deploy to Streamlit Community Cloud

1. **Sign up/Login to Streamlit**
   - Go to https://share.streamlit.io/
   - Sign in with GitHub

2. **Deploy your app**
   - Click "New app"
   - Select your repository: `YOUR_USERNAME/msjstocktrader`
   - Main file path: `trading_app.py`
   - Click "Deploy"

3. **Configure Secrets (IMPORTANT)**
   - In your app dashboard, click ⚙️ **Settings**
   - Click **Secrets**
   - Add the following:

   ```toml
   # Gmail Configuration (for sending emails)
   GMAIL_EMAIL = "your-email@gmail.com"
   GMAIL_APP_PASSWORD = "your-16-char-app-password"
   ```

### Step 3: Get Gmail App Password

To enable email functionality:

1. Go to https://myaccount.google.com/security
2. Enable **2-Step Verification** (if not enabled)
3. Go to https://myaccount.google.com/apppasswords
4. Create new app password:
   - App: "Mail"
   - Device: "Other (MSJSTOCKTRADER)"
5. **Copy the 16-character password**
6. Add it to Streamlit Secrets as `GMAIL_APP_PASSWORD`

## 📋 What's Included

```
msjstocktrader/
├── trading_app.py              # Main application
├── requirements.txt            # Python dependencies
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── modules/
│   ├── auth.py                # Authentication
│   ├── trading_engine.py      # Trading logic
│   ├── portfolio_manager.py   # Portfolio management
│   ├── market_data.py         # Yahoo Finance integration
│   ├── email_service.py       # Email notifications
│   ├── demo_manager.py        # Demo account
│   ├── competition_manager.py # Competition system
│   └── [other modules]
├── data/
│   ├── users.json             # User accounts
│   ├── portfolios.json        # Portfolio data
│   ├── trades.json            # Trading history
│   ├── positions.json         # Current positions
│   └── [other data files]
└── README.md                  # This file
```

## 🔧 Configuration

### Required Environment Variables (Streamlit Secrets)

```toml
# Email Configuration
GMAIL_EMAIL = "your-email@gmail.com"
GMAIL_APP_PASSWORD = "your-app-password"
```

### Optional: Custom Domain

To use a custom domain:
1. Go to app settings
2. Click "Custom domain"
3. Follow Streamlit's instructions

## ✅ Features

- **Live Market Data**: Real-time US stock prices via Yahoo Finance (340+ tickers)
- **6-Month Competitions**: Automated trading competitions with winners
- **Short Selling**: Support for short positions
- **Email Notifications**: Welcome emails, team invitations, announcements
- **Demo Account**: 5-minute demo sessions
- **Leaderboards**: Global rankings and team competitions
- **Badge System**: 25+ achievement badges
- **Admin Panel**: Super admin controls

## 🎯 Default Super Admin

- **Email**: ayagar624@gmail.com
- **Username**: Ayaan Garg
- **Password**: 78muydwnEY+-i8Y

**⚠️ IMPORTANT**: Change the super admin password immediately after first login!

## 🔒 Security Notes

1. **Never commit secrets to GitHub**
   - All secrets go in Streamlit Secrets
   - `.gitignore` is configured to exclude sensitive files

2. **Change default passwords**
   - Update super admin credentials
   - Use strong passwords for all accounts

3. **Email security**
   - Use Gmail App Passwords (not your actual password)
   - Enable 2-Step Verification on your Google account

## 🐛 Troubleshooting

### App won't start
- Check that `requirements.txt` includes all dependencies
- Verify Streamlit Secrets are configured correctly
- Check logs in Streamlit dashboard

### Emails not sending
- Verify `GMAIL_EMAIL` and `GMAIL_APP_PASSWORD` are correct
- Make sure 2-Step Verification is enabled
- App password should be 16 characters (no spaces)

### Database issues
- The app auto-creates JSON files in `data/` folder
- Initial data is included in the package
- Data persists between deployments

## 📊 System Requirements

- **Python**: 3.11+
- **Memory**: 1GB minimum
- **Storage**: 500MB minimum
- **Network**: Stable internet for Yahoo Finance API

## 🆘 Support

For issues or questions:
- Check Streamlit logs in the dashboard
- Review error messages carefully
- Ensure all secrets are configured

## 📝 License

All rights reserved. Educational and demonstration purposes only.

---

**Built with ❤️ using Streamlit, Yahoo Finance API, and Python**

🎉 **You're all set! Your MSJSTOCKTRADER platform is ready to go live!**
