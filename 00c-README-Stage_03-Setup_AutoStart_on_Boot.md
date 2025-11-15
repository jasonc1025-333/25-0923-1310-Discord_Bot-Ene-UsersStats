# Auto-Start Discord Bot on Linux Boot

## 🚀 Setup Discord Bot as Systemd Service

This guide shows you how to configure your Discord bot to automatically start when your Linux system boots, and restart automatically if it crashes.

---

## 📋 Quick Setup (TL;DR)

```bash
# 1. Create service file
sudo nano /etc/systemd/system/discord-bot-usersstats.service

# 2. Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable discord-bot-usersstats.service
sudo systemctl start discord-bot-usersstats.service

# 3. Check status
sudo systemctl status discord-bot-usersstats.service
```

---

## 📝 Step-by-Step Instructions

### Step 1: Create Systemd Service File

Create a new service file for your Discord bot:

```bash
sudo nano /etc/systemd/system/discord-bot-usersstats.service
```

**Copy and paste this content** (adjust paths if needed):

```ini
[Unit]
Description=Discord Bot Users Stats - Real-time Analytics Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=jasonc1025
Group=jasonc1025
WorkingDirectory=/home/jasonc1025/Jwc-25-0514-2300-Bmax_B1Pro-Ubuntu_22/12j-Db/Dropbox/09l-Lin-SM/25-0923-1310-Discord_Bot-Ene-UsersStats
ExecStart=/home/jasonc1025/Jwc-25-0514-2300-Bmax_B1Pro-Ubuntu_22/12j-Db/Dropbox/09l-Lin-SM/25-0923-1310-Discord_Bot-Ene-UsersStats/venv/bin/python /home/jasonc1025/Jwc-25-0514-2300-Bmax_B1Pro-Ubuntu_22/12j-Db/Dropbox/09l-Lin-SM/25-0923-1310-Discord_Bot-Ene-UsersStats/11-DiscordBot-Users_Stats-RunMe-ForDiscordUsers.py

# Restart policy
Restart=always
RestartSec=10

# Security and resource limits
StandardOutput=journal
StandardError=journal
SyslogIdentifier=discord-bot-usersstats

# Environment
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
```

**Save the file:**
- Press `Ctrl+O` to save
- Press `Enter` to confirm
- Press `Ctrl+X` to exit

---

### Step 2: Enable and Start the Service

```bash
# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable discord-bot-usersstats.service

# Start the service now
sudo systemctl start discord-bot-usersstats.service
```

---

### Step 3: Verify Service is Running

```bash
# Check service status
sudo systemctl status discord-bot-usersstats.service
```

**Expected output:**
```
● discord-bot-usersstats.service - Discord Bot Users Stats - Real-time Analytics Bot
     Loaded: loaded (/etc/systemd/system/discord-bot-usersstats.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2025-11-15 02:15:00 PST; 5s ago
   Main PID: 12345 (python)
      Tasks: 3 (limit: 18933)
     Memory: 45.2M
        CPU: 1.234s
     CGroup: /system.slice/discord-bot-usersstats.service
             └─12345 /home/jasonc1025/.../venv/bin/python ...
```

Look for **"Active: active (running)"** - this means your bot is running!

---

## 🎮 Managing Your Service

### Basic Commands

```bash
# Start the bot
sudo systemctl start discord-bot-usersstats.service

# Stop the bot
sudo systemctl stop discord-bot-usersstats.service

# Restart the bot (useful after making changes)
sudo systemctl restart discord-bot-usersstats.service

# Check status
sudo systemctl status discord-bot-usersstats.service

# View recent logs
sudo journalctl -u discord-bot-usersstats.service -n 50

# Follow logs in real-time (like tail -f)
sudo journalctl -u discord-bot-usersstats.service -f

# View logs with timestamps
sudo journalctl -u discord-bot-usersstats.service --since "10 minutes ago"
```

### Enable/Disable Auto-Start

```bash
# Enable auto-start on boot (if not already enabled)
sudo systemctl enable discord-bot-usersstats.service

# Disable auto-start on boot
sudo systemctl disable discord-bot-usersstats.service

# Check if enabled
sudo systemctl is-enabled discord-bot-usersstats.service
```

---

## 📊 Viewing Logs

### Real-time Log Monitoring

```bash
# Follow logs in real-time (press Ctrl+C to exit)
sudo journalctl -u discord-bot-usersstats.service -f
```

### View Recent Logs

```bash
# Last 50 lines
sudo journalctl -u discord-bot-usersstats.service -n 50

# Last 100 lines
sudo journalctl -u discord-bot-usersstats.service -n 100

# All logs from today
sudo journalctl -u discord-bot-usersstats.service --since today

# Logs from specific time
sudo journalctl -u discord-bot-usersstats.service --since "2025-11-15 00:00:00"

# Logs from last hour
sudo journalctl -u discord-bot-usersstats.service --since "1 hour ago"
```

### Advanced Log Viewing

```bash
# Show logs with full details
sudo journalctl -u discord-bot-usersstats.service -xe

# Export logs to file
sudo journalctl -u discord-bot-usersstats.service > bot-logs.txt

# View logs in reverse order (newest first)
sudo journalctl -u discord-bot-usersstats.service -r
```

---

## 🔧 Updating Your Bot

When you make changes to your bot code, you need to restart the service:

```bash
# Method 1: Restart the service
sudo systemctl restart discord-bot-usersstats.service

# Method 2: Stop and start (more thorough)
sudo systemctl stop discord-bot-usersstats.service
sudo systemctl start discord-bot-usersstats.service

# Verify it's running with new changes
sudo systemctl status discord-bot-usersstats.service
```

---

## 🔐 Security Considerations

### File Permissions

Ensure your service file has correct permissions:

```bash
sudo chmod 644 /etc/systemd/system/discord-bot-usersstats.service
```

### Environment File Security

Protect your bot token:

```bash
chmod 600 .env-SecretDiscordBotToken-NotPublishToGithub
```

### Running as Non-Root User

The service runs as your user (`jasonc1025`), which is more secure than running as root.

---

## 🛠️ Troubleshooting

### Service Won't Start

**Check service status for errors:**
```bash
sudo systemctl status discord-bot-usersstats.service
```

**View detailed logs:**
```bash
sudo journalctl -u discord-bot-usersstats.service -xe
```

**Common issues:**

1. **Wrong file paths in service file**
   ```bash
   # Verify paths exist
   ls -la /home/jasonc1025/Jwc-25-0514-2300-Bmax_B1Pro-Ubuntu_22/12j-Db/Dropbox/09l-Lin-SM/25-0923-1310-Discord_Bot-Ene-UsersStats/venv/bin/python
   ls -la /home/jasonc1025/Jwc-25-0514-2300-Bmax_B1Pro-Ubuntu_22/12j-Db/Dropbox/09l-Lin-SM/25-0923-1310-Discord_Bot-Ene-UsersStats/11-DiscordBot-Users_Stats-RunMe-ForDiscordUsers.py
   ```

2. **Missing bot token**
   ```bash
   # Check if .env file exists and has token
   cat .env-SecretDiscordBotToken-NotPublishToGithub
   ```

3. **Permission issues**
   ```bash
   # Make sure you own the files
   ls -la /home/jasonc1025/Jwc-25-0514-2300-Bmax_B1Pro-Ubuntu_22/12j-Db/Dropbox/09l-Lin-SM/25-0923-1310-Discord_Bot-Ene-UsersStats/
   ```

4. **Network not ready**
   - The service waits for network (network-online.target)
   - Check if network is working: `ping google.com`

### Service Keeps Restarting

```bash
# Check why it's restarting
sudo journalctl -u discord-bot-usersstats.service -n 100

# Common causes:
# - Invalid bot token
# - Missing dependencies
# - Python errors in code
```

### Reload Service After Changes

If you edit the service file, reload systemd:

```bash
sudo systemctl daemon-reload
sudo systemctl restart discord-bot-usersstats.service
```

---

## 📈 Service Configuration Explained

### Service File Breakdown

```ini
[Unit]
Description=Discord Bot Users Stats - Real-time Analytics Bot
# Human-readable description

After=network-online.target
# Wait for network to be ready before starting

Wants=network-online.target
# Prefer network, but don't fail if not available

[Service]
Type=simple
# Simple long-running process

User=jasonc1025
Group=jasonc1025
# Run as your user (not root)

WorkingDirectory=/path/to/bot
# Bot's working directory

ExecStart=/path/to/venv/bin/python /path/to/script.py
# Command to start the bot

Restart=always
# Always restart if bot crashes

RestartSec=10
# Wait 10 seconds before restarting

StandardOutput=journal
StandardError=journal
# Send output to systemd journal

SyslogIdentifier=discord-bot-usersstats
# Identifier for logs

Environment="PYTHONUNBUFFERED=1"
# Ensure Python output is not buffered

[Install]
WantedBy=multi-user.target
# Start in multi-user mode (normal boot)
```

### Restart Policies

You can customize the restart behavior:

```ini
# Always restart (current setting)
Restart=always

# Only restart on failure
Restart=on-failure

# Never restart
Restart=no

# Restart unless stopped manually
Restart=unless-stopped
```

### Restart Timing

```ini
# Wait time before restart
RestartSec=10

# Maximum restart attempts
StartLimitBurst=5

# Time window for counting restarts
StartLimitIntervalSec=300
```

---

## 🚦 Testing Auto-Start

### Test 1: Reboot Test

```bash
# Reboot your system
sudo reboot

# After reboot, check if bot is running
sudo systemctl status discord-bot-usersstats.service

# Should show "Active: active (running)"
```

### Test 2: Manual Stop/Start

```bash
# Stop the bot
sudo systemctl stop discord-bot-usersstats.service

# Verify it's stopped
sudo systemctl status discord-bot-usersstats.service

# Start it again
sudo systemctl start discord-bot-usersstats.service

# Verify it's running
sudo systemctl status discord-bot-usersstats.service
```

### Test 3: Crash Recovery

```bash
# Get the process ID
sudo systemctl status discord-bot-usersstats.service | grep "Main PID"

# Kill the process (simulating a crash)
sudo kill -9 [PID]

# Wait 10 seconds, then check status
sleep 10
sudo systemctl status discord-bot-usersstats.service

# Should show it restarted automatically
```

---

## 🌟 Advanced Features

### Email Notifications on Failure

Install mail utilities:
```bash
sudo apt install mailutils
```

Edit service file to add:
```ini
[Service]
OnFailure=notify-email@%i.service
```

### Resource Limits

Add to `[Service]` section:
```ini
# Limit memory usage to 500MB
MemoryMax=500M

# Limit CPU usage to 50%
CPUQuota=50%

# Set CPU priority (nice value)
Nice=10
```

### Multiple Bot Instances

Create separate service files for different bots:
```bash
/etc/systemd/system/discord-bot-1.service
/etc/systemd/system/discord-bot-2.service
/etc/systemd/system/discord-bot-3.service
```

---

## 🔄 Alternative: Using Screen (Quick & Easy)

If you prefer not to use systemd, you can use `screen`:

### Setup Screen Session

```bash
# Install screen
sudo apt install screen

# Start a new screen session for your bot
screen -S discord-bot

# Inside screen, activate venv and run bot
cd /home/jasonc1025/Jwc-25-0514-2300-Bmax_B1Pro-Ubuntu_22/12j-Db/Dropbox/09l-Lin-SM/25-0923-1310-Discord_Bot-Ene-UsersStats
venv/bin/python 11-DiscordBot-Users_Stats-RunMe-ForDiscordUsers.py

# Detach from screen: Press Ctrl+A, then D

# Reattach later
screen -r discord-bot

# List all screen sessions
screen -ls
```

**Note:** Screen sessions don't survive reboots. Use systemd for true auto-start on boot.

---

## 📚 Quick Reference

### Most Common Commands

```bash
# Start bot
sudo systemctl start discord-bot-usersstats.service

# Stop bot
sudo systemctl stop discord-bot-usersstats.service

# Restart bot
sudo systemctl restart discord-bot-usersstats.service

# Check status
sudo systemctl status discord-bot-usersstats.service

# View logs
sudo journalctl -u discord-bot-usersstats.service -f

# Enable auto-start
sudo systemctl enable discord-bot-usersstats.service

# Disable auto-start
sudo systemctl disable discord-bot-usersstats.service
```

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Service file created at `/etc/systemd/system/discord-bot-usersstats.service`
- [ ] Service enabled: `sudo systemctl is-enabled discord-bot-usersstats.service` shows "enabled"
- [ ] Service running: `sudo systemctl status discord-bot-usersstats.service` shows "active (running)"
- [ ] Logs visible: `sudo journalctl -u discord-bot-usersstats.service` shows output
- [ ] Bot responds in Discord: Test with `!stats_help` command
- [ ] Reboot test: Bot starts automatically after `sudo reboot`
- [ ] Crash recovery: Bot restarts automatically after manual kill

---

## 🎯 Benefits of Systemd Service

✅ **Automatic start on boot** - No manual intervention needed  
✅ **Auto-restart on crash** - Bot recovers automatically  
✅ **Centralized logging** - All logs in systemd journal  
✅ **Easy management** - Simple start/stop/restart commands  
✅ **Resource control** - Can limit CPU, memory usage  
✅ **Security** - Runs as non-root user  
✅ **Standard Linux practice** - Professional deployment method  

---

**Created:** 2025-11-15  
**Last Updated:** 2025-11-15  
**For:** Discord Bot Users Stats (11-DiscordBot-Users_Stats-RunMe-ForDiscordUsers.py)  
**OS:** Ubuntu 22.04 / Linux
