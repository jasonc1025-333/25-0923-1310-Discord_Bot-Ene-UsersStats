# Linux Setup Guide for Discord Bot User Stats

## Quick Start (TL;DR)

```bash
# Run the script directly (virtual environment already set up):
venv/bin/python 01-DiscordBot-Users_Stats-RunMe-ForAdminExternalConsole.py

# OR activate virtual environment first:
source venv/bin/activate
python 01-DiscordBot-Users_Stats-RunMe-ForAdminExternalConsole.py
deactivate  # when done
```

---

## Complete Setup Instructions

### ✅ Already Completed (First-time Setup)

The following has already been done for you:

1. **Python 3.10.12** is installed and available
2. **Virtual environment** created at `./venv`
3. **Dependencies installed**:
   - discord.py >= 2.3.0
   - python-dotenv >= 1.0.0
4. **Environment variables** configured in `.env-SecretDiscordBotToken-NotPublishToGithub`

---

## 📋 Manual Setup Instructions (From Scratch)

If you need to set this up again from scratch or on another Linux machine, follow these steps:

### Step 1: Verify Python Installation

```bash
# Check if Python 3 is installed (Python 3.7+ required)
python3 --version

# If not installed, install it (Ubuntu/Debian):
sudo apt update
sudo apt install python3 python3-venv python3-pip

# For other distributions:
# Fedora/RHEL: sudo dnf install python3 python3-pip
# Arch: sudo pacman -S python python-pip
```

### Step 2: Create Virtual Environment

```bash
# Navigate to your project directory
cd /path/to/25-0923-1310-Discord_Bot-Ene-UsersStats--OPENED-25-1113-1900-MoveToDb

# Create virtual environment named 'venv'
python3 -m venv venv

# Verify virtual environment was created
ls -la venv
```

**What this does:**
- Creates an isolated Python environment in the `venv` directory
- Prevents conflicts with system-wide Python packages
- Allows you to install project-specific dependencies

### Step 3: Install Dependencies

**Option A: Direct installation (without activating environment)**
```bash
venv/bin/pip install -r requirements.txt
```

**Option B: Activate environment first, then install**
```bash
# Activate virtual environment
source venv/bin/activate

# Your prompt should change to show (venv)
# Install dependencies
pip install -r requirements.txt

# Verify installations
pip list

# Deactivate when done
deactivate
```

**What gets installed:**
- `discord.py>=2.3.0` - Discord API wrapper for Python
- `python-dotenv>=1.0.0` - Loads environment variables from .env files

### Step 4: Configure Environment Variables

```bash
# Option A: Copy the template file
cp .env.TEMPLATE-BLANK .env-SecretDiscordBotToken-NotPublishToGithub

# Option B: Create the file manually
nano .env-SecretDiscordBotToken-NotPublishToGithub
```

**Add the following content:**
```bash
# Discord Bot Configuration
DISCORD_BOT_TOKEN=your_actual_bot_token_here
DEBUG_MODE=true
RENDER_DOT_COM__WEB_SERVICE=false
```

**To get your Discord Bot Token:**
1. Go to https://discord.com/developers/applications
2. Select your application (or create a new one)
3. Go to "Bot" section
4. Click "Reset Token" to generate a new token
5. Copy the token and paste it in your .env file

**Important Security Note:**
- Never commit `.env-SecretDiscordBotToken-NotPublishToGithub` to Git
- Keep your bot token secret
- The `.gitignore` file should already exclude this file

### Step 5: Make Script Executable (Optional)

```bash
# Make the script executable
chmod +x 01-DiscordBot-Users_Stats-RunMe-ForAdminExternalConsole.py

# Now you can run it directly
./01-DiscordBot-Users_Stats-RunMe-ForAdminExternalConsole.py
```

---

## 🚀 Running the Script

### Method 1: Direct Execution (Recommended)

Run the script directly using the virtual environment's Python interpreter:

```bash
venv/bin/python 01-DiscordBot-Users_Stats-RunMe-ForAdminExternalConsole.py
```

**Why this method?**
- No need to activate/deactivate the environment
- Works in scripts and automation
- Clear which Python interpreter is being used

### Method 2: With Virtual Environment Activated

Activate the virtual environment, then run with the regular python command:

```bash
# Activate virtual environment
source venv/bin/activate

# Your prompt should now show (venv)
# Run the script
python 01-DiscordBot-Users_Stats-RunMe-ForAdminExternalConsole.py

# When done, deactivate
deactivate
```

---

## 🎯 Command Line Options

The script supports date range filtering for analyzing specific time periods:

### Analyze All Messages (Default)
```bash
venv/bin/python 01-DiscordBot-Users_Stats-RunMe-ForAdminExternalConsole.py
```

### Analyze from a Start Date
```bash
venv/bin/python 01-DiscordBot-Users_Stats-RunMe-ForAdminExternalConsole.py --start=2024-01-01
```

### Analyze Messages in a Date Range
```bash
venv/bin/python 01-DiscordBot-Users_Stats-RunMe-ForAdminExternalConsole.py --start=2024-01-01 --end=2024-12-31
```

### Analyze Until an End Date
```bash
venv/bin/python 01-DiscordBot-Users_Stats-RunMe-ForAdminExternalConsole.py --end=2023-12-31
```

### Show Help
```bash
venv/bin/python 01-DiscordBot-Users_Stats-RunMe-ForAdminExternalConsole.py --help
```

---

## 🔑 Key Differences: Windows vs Linux

Understanding these differences helps when migrating from Windows:

| Aspect | Windows | Linux |
|--------|---------|-------|
| **Python command** | `python` | `python3` |
| **Path separator** | `\` (backslash) | `/` (forward slash) |
| **Virtual env activation** | `venv\Scripts\activate` | `source venv/bin/activate` |
| **Virtual env python** | `venv\Scripts\python.exe` | `venv/bin/python` |
| **Virtual env pip** | `venv\Scripts\pip.exe` | `venv/bin/pip` |
| **Line endings** | CRLF (`\r\n`) | LF (`\n`) |
| **Case sensitivity** | Files not case-sensitive | Files ARE case-sensitive |
| **Executable files** | `.exe`, `.bat` | No extension, use `chmod +x` |
| **Home directory** | `C:\Users\username` | `/home/username` |
| **Shebang line** | Not used | `#!/usr/bin/env python3` |

---

## 📂 Project Structure

```
25-0923-1310-Discord_Bot-Ene-UsersStats--OPENED-25-1113-1900-MoveToDb/
├── 01-DiscordBot-Users_Stats-RunMe-ForAdminExternalConsole.py  # Main script
├── 11-DiscordBot-Users_Stats-RunMe-ForDiscordUsers.py          # User-facing bot
├── requirements.txt                                            # Python dependencies
├── .env-SecretDiscordBotToken-NotPublishToGithub              # Bot token (secret)
├── .env.TEMPLATE-BLANK                                         # Environment template
├── .gitignore                                                  # Git ignore rules
├── README.md                                                   # Project documentation
├── LINUX_SETUP_GUIDE.md                                       # This file
├── venv/                                                       # Virtual environment
├── logs/                                                       # Log files
└── 02-DiscordBot-Users_Stats-DataReport_Output.json          # Generated report
```

---

## 📊 Output Files

The script generates the following output:

### 1. Terminal Output
- Real-time progress updates during scanning
- Comprehensive analytics report with:
  - Summary statistics
  - User leaderboards (messages, reactions given/received)
  - Detailed per-user statistics
  - Top emojis used by each user

### 2. JSON Data File
- **File:** `02-DiscordBot-Users_Stats-DataReport_Output.json`
- **Contents:** Raw analytics data in JSON format
- **Use:** Can be processed by other scripts or imported into databases

---

## 🔧 Troubleshooting

### Virtual Environment Issues

**Problem:** `python3 -m venv venv` fails
```bash
# Solution: Install python3-venv package
sudo apt install python3-venv

# Then try again
python3 -m venv venv
```

**Problem:** Virtual environment is corrupted
```bash
# Solution: Delete and recreate
rm -rf venv
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

### Permission Issues

**Problem:** "Permission Denied" when running script
```bash
# Solution: Make script executable
chmod +x 01-DiscordBot-Users_Stats-RunMe-ForAdminExternalConsole.py

# Or run with python directly
venv/bin/python 01-DiscordBot-Users_Stats-RunMe-ForAdminExternalConsole.py
```

### Discord Bot Issues

**Problem:** "DISCORD_BOT_TOKEN not found!"
```bash
# Solution: Verify environment file exists and has correct content
cat .env-SecretDiscordBotToken-NotPublishToGithub

# Make sure it contains:
# DISCORD_BOT_TOKEN=your_actual_token
```

**Problem:** "Forbidden" or "No permission to read channel"
```bash
# Solution: Check bot permissions in Discord Developer Portal
# Required permissions:
# - Read Message History
# - View Channels
# - Read Messages/View Channels
#
# Required intents (enable in Developer Portal):
# - Message Content Intent
# - Server Members Intent
```

**Problem:** Bot token is invalid
```bash
# Solution: Generate a new token
# 1. Go to https://discord.com/developers/applications
# 2. Select your application
# 3. Go to "Bot" section
# 4. Click "Reset Token"
# 5. Copy new token to .env file
```

### Dependency Issues

**Problem:** `discord.py` fails to install
```bash
# Solution: Update pip and try again
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt

# If still fails, install specific version
venv/bin/pip install discord.py==2.3.0
```

**Problem:** Missing system dependencies
```bash
# Solution: Install required system packages (Ubuntu/Debian)
sudo apt update
sudo apt install build-essential python3-dev

# For other distributions, install equivalent development packages
```

### SSL/Network Issues

**Problem:** SSL certificate errors
```bash
# Solution: Update CA certificates
sudo apt update
sudo apt install ca-certificates
sudo update-ca-certificates
```

**Problem:** "Unclosed connector" warnings at end of script
```bash
# This is a known harmless warning with discord.py
# The script still completes successfully
# You can safely ignore these warnings
```

---

## 🔐 Security Best Practices

1. **Never commit your bot token**
   - The `.env-SecretDiscordBotToken-NotPublishToGithub` file should be in `.gitignore`
   - If accidentally committed, regenerate your token immediately

2. **File permissions**
   ```bash
   # Make environment file readable only by owner
   chmod 600 .env-SecretDiscordBotToken-NotPublishToGithub
   ```

3. **Keep dependencies updated**
   ```bash
   # Check for outdated packages
   venv/bin/pip list --outdated
   
   # Update specific package
   venv/bin/pip install --upgrade discord.py
   
   # Update all packages (be careful!)
   venv/bin/pip install --upgrade -r requirements.txt
   ```

4. **Bot token rotation**
   - Regularly regenerate your bot token
   - Update the token in your environment file
   - Never share your token with anyone

---

## 📝 Maintenance

### Updating Dependencies

```bash
# Check current versions
venv/bin/pip list

# Update a specific package
venv/bin/pip install --upgrade discord.py

# Update all packages
venv/bin/pip install --upgrade -r requirements.txt

# Freeze current versions (for reproducibility)
venv/bin/pip freeze > requirements.txt
```

### Backing Up Data

```bash
# Backup the JSON output
cp 02-DiscordBot-Users_Stats-DataReport_Output.json \
   backups/report-$(date +%Y%m%d-%H%M%S).json

# Backup logs
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/
```

### Cleaning Up

```bash
# Remove old log files (older than 30 days)
find logs/ -name "*.log" -mtime +30 -delete

# Clean Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

---

## 🚀 Advanced Usage

### Running in Background

```bash
# Run in background with nohup
nohup venv/bin/python 01-DiscordBot-Users_Stats-RunMe-ForAdminExternalConsole.py > output.log 2>&1 &

# Or use screen
screen -S discord-bot
venv/bin/python 01-DiscordBot-Users_Stats-RunMe-ForAdminExternalConsole.py
# Press Ctrl+A, then D to detach
# Reattach with: screen -r discord-bot
```

### Scheduled Execution with Cron

```bash
# Edit crontab
crontab -e

# Run daily at 2 AM
0 2 * * * cd /path/to/discord/bot && venv/bin/python 01-DiscordBot-Users_Stats-RunMe-ForAdminExternalConsole.py >> logs/cron.log 2>&1
```

### Creating a Shell Script Wrapper

```bash
# Create run-bot.sh
cat > run-bot.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
venv/bin/python 01-DiscordBot-Users_Stats-RunMe-ForAdminExternalConsole.py "$@"
EOF

# Make executable
chmod +x run-bot.sh

# Now you can run
./run-bot.sh --start=2024-01-01
```

---

## 📚 Additional Resources

- **Discord.py Documentation:** https://discordpy.readthedocs.io/
- **Discord Developer Portal:** https://discord.com/developers/applications
- **Python Virtual Environments:** https://docs.python.org/3/library/venv.html
- **Project GitHub:** https://github.com/jasonc1025-333/25-0923-1310-Discord_Bot-Ene-UsersStats

---

## ✅ Quick Checklist for New Setup

- [ ] Python 3.7+ installed (`python3 --version`)
- [ ] Virtual environment created (`python3 -m venv venv`)
- [ ] Dependencies installed (`venv/bin/pip install -r requirements.txt`)
- [ ] Environment file created (`.env-SecretDiscordBotToken-NotPublishToGithub`)
- [ ] Bot token added to environment file
- [ ] Bot has correct permissions in Discord
- [ ] Privileged intents enabled in Discord Developer Portal
- [ ] Script runs successfully (`venv/bin/python 01-DiscordBot-Users_Stats-RunMe-ForAdminExternalConsole.py`)
- [ ] Output JSON file generated
- [ ] Report displays in terminal

---

**Last Updated:** November 14, 2025  
**Python Version Tested:** 3.10.12  
**OS Tested:** Ubuntu 22.04 (Linux 6.8)
