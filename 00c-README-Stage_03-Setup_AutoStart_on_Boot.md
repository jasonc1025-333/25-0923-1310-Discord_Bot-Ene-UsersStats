# Auto-Start Discord Bot on Linux Boot

Configure your Discord bot to automatically start on system boot using systemd.

---

## 🚀 Quick Setup

```bash
# 1. Copy service file to systemd
sudo cp 10-SetupFileFor-etc_systemd_system/discord-bot-usersstats.service /etc/systemd/system/

# 2. Enable and start
sudo systemctl daemon-reload
sudo systemctl enable discord-bot-usersstats.service
sudo systemctl start discord-bot-usersstats.service

# 3. Verify
sudo systemctl status discord-bot-usersstats.service
```

**Look for:** `Active: active (running)` ✅

---

## 📝 Manual Setup (If Needed)

If the service file doesn't exist, create it:

```bash
sudo nano /etc/systemd/system/discord-bot-usersstats.service
```

Paste this content **(adjust User and paths for your system)**:

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

Save: `Ctrl+O`, `Enter`, `Ctrl+X`

---

## 🎮 Common Commands

```bash
# Start/Stop/Restart
sudo systemctl start discord-bot-usersstats.service
sudo systemctl stop discord-bot-usersstats.service
sudo systemctl restart discord-bot-usersstats.service

# Status
sudo systemctl status discord-bot-usersstats.service

# Enable/Disable auto-start on boot
sudo systemctl enable discord-bot-usersstats.service
sudo systemctl disable discord-bot-usersstats.service
```

---

## 📊 View Logs

```bash
# Real-time logs (Ctrl+C to exit)
sudo journalctl -u discord-bot-usersstats.service -f

# Last 50 lines
sudo journalctl -u discord-bot-usersstats.service -n 50

# Logs from last hour
sudo journalctl -u discord-bot-usersstats.service --since "1 hour ago"

# All logs from today
sudo journalctl -u discord-bot-usersstats.service --since today
```

---

## 🔧 After Code Updates

Restart the service to apply changes:

```bash
sudo systemctl restart discord-bot-usersstats.service
sudo systemctl status discord-bot-usersstats.service
```

---

## 🛠️ Troubleshooting

### Service Won't Start

1. **Check logs for errors:**
   ```bash
   sudo journalctl -u discord-bot-usersstats.service -n 100
   ```

2. **Common issues:**
   - ❌ **Wrong paths:** Verify paths in service file match your system
   - ❌ **Missing bot token:** Check `.env-SecretDiscordBotToken-NotPublishToGithub`
   - ❌ **Permission issues:** Ensure files are owned by your user
   - ❌ **Network not ready:** Service waits for network (usually auto-resolves)

3. **After fixing, reload:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart discord-bot-usersstats.service
   ```

### Service Keeps Restarting

Check logs for Python errors:
```bash
sudo journalctl -u discord-bot-usersstats.service -n 200
```

Common causes: Invalid bot token, missing dependencies, code errors

---

## ✅ Verification Checklist

- [ ] Service enabled: `sudo systemctl is-enabled discord-bot-usersstats.service` → "enabled"
- [ ] Service running: `sudo systemctl status discord-bot-usersstats.service` → "active (running)"
- [ ] Bot responds in Discord: Test with `!stats_help`
- [ ] Auto-start works: Reboot and verify bot starts automatically

---

## 🎯 Benefits

✅ **Auto-start on boot** - No manual intervention  
✅ **Auto-restart on crash** - Self-healing  
✅ **Centralized logging** - All logs in one place  
✅ **Easy management** - Simple commands  
✅ **Professional deployment** - Industry standard  

---

**For:** Discord Bot Users Stats (`11-DiscordBot-Users_Stats-RunMe-ForDiscordUsers.py`)  
**OS:** Ubuntu 22.04 / Linux  
**Last Updated:** 2025-11-15
