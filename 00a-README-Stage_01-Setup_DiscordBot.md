# Discord Analytics - Standalone Admin Report Generator

# IMPORTANT NOTES
- jwc 25-1115-2100 For 'news_main', '!stats' failed to retrieve full_history, 
  - so needed to increase 'History Scan Limit' from 1,000 to 10,000 and deleting '12-DiscordBot-Users_Stats-DataReport_Output.json' to force a new full-rescan  

A comprehensive Discord analytics tool that scans all server channels and generates detailed admin reports of user activity including message counts and emoji reaction usage.

## Features

- **Complete Historical Analysis**: Scans ALL messages and reactions across ALL channels
- **Comprehensive User Statistics**: Detailed breakdown per user with real display names
- **Admin-Only Terminal Reports**: Private reports that don't appear in Discord
- **One-Time Execution**: Runs once, generates report, and terminates automatically
- **Cross-Server Analysis**: Analyzes all servers the bot has access to
- **Alphabetical User Ordering**: Users sorted alphabetically for easy reference
- **Real-Time Progress Indicators**: Progress updates at 10% increments and every 5 messages show scanning status and confirm script is running

## What You Get

- **Summary Statistics**: Total users, channels, messages, and reactions
- **Top 10 Leaderboards**: Message senders, reaction givers, and reaction receivers
- **Detailed User Reports**: Complete stats for each user in alphabetical order
- **Emoji Analysis**: Top emojis given and received per user
- **Channel Activity**: Number of channels each user is active in
- **Data Export**: All data saved to `02-DiscordBot-Users_Stats-DataReport_Output.json` for future reference

## Setup Instructions

### 1. Create a Discord Bot

   1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
   2. Click "New Application" and give it a name
   3. Go to the "Bot" section in the left sidebar (NOT "General Information")
   4. Click "Add Bot" if you haven't already
   5. Under the "Token" section, click "Reset Token" or "Copy" to get your bot token
      - **Important**: This is NOT the Application ID or Public Key from "General Information"
      - The bot token is a long string that looks like: 
         - 25-1109-1100 `MTQ...Z_0`
         - 25-1110-2030 'MTQ...f7E'
         - 25-1110-2100 For Render.com, Move to its 'Environment Variable: DISCORD_BOT_TOKEN' 
            - *** For Security, if keep in GitHub, have repository be private.
      - You may need to click "Reset Token" to generate a new one if this is your first time
   6. Copy this token (you'll need this for the .env file)

### 2. Set Bot Permissions and Invite Bot to Server

   In the Discord Developer Portal, go to the "OAuth2" > "URL Generator" section:

   **Step-by-step process:**

   1. **Select Scopes:**
      - Check the `bot` checkbox

   2. **Select Bot Permissions:**
      - `Send Messages`
      - `Use Slash Commands`
      - `Read Message History`
      - `Add Reactions`
      - `Use External Emojis`
      - `Embed Links`

   3. **Copy the Generated URL:**
      - At the bottom of the page, Discord automatically generates an invitation URL
      - It looks like: `https://discord.com/api/oauth2/authorize?client_id=123456789012345678&permissions=2048&scope=bot`
         - 25-1110-1030 https://discord.com/oauth2/authorize?client_id=1437143803046793378&permissions=2147829824&integration_type=0&scope=bot
      - Click the "Copy" button next to this URL

   4. **Use the URL to Invite the Bot:**
      - **Paste the URL into your web browser** and press Enter
      - **Select your Discord server** from the dropdown (you need "Manage Server" permissions)
      - **Review the permissions** that will be granted to the bot
      - **Click "Authorize"** to add the bot to your server
      - **Complete any captcha** verification if prompted

   5. **Verify the Bot was Added:**
      - The bot will appear in your server's member list (it will show as offline until you run the bot code)
      - You should see a message in your server saying the bot was added

   **Important:** You must have administrator privileges or "Manage Server" permissions to invite bots to a Discord server.

### 3. Install Dependencies

   ```bash
   pip install -r requirements.txt
   ```

### 4. Configure the Bot

   1. Copy `.env.example` to `.env`:
      ```bash
      cp .env.example .env
      ```

   2. Edit `.env` and add your bot token:
      ```
      DISCORD_BOT_TOKEN=your_actual_bot_token_here
      ```

### 5. Run the Analytics Report

   ```bash
   python 01-DiscordBot-Users_Stats-RunMe.py
   ```

   **This single command does everything:**
   - Connects to Discord using your bot token
   - Scans ALL channels in ALL servers the bot has access to
   - Analyzes ALL historical messages and reactions
   - Generates a comprehensive terminal report
   - Saves data to `02-DiscordBot-Users_Stats-DataReport_Output.json`
   - Automatically terminates when complete

## How It Works

   1. **Connects to Discord** - Uses your bot token to authenticate
   2. **Scans All Servers** - Analyzes every server the bot has been invited to
   3. **Reads All Channels** - Goes through every text channel it has permission to read
   4. **Collects Historical Data** - Scans all existing messages and reactions (no limits)
   5. **Caches User Names** - Stores real Discord display names for readable reports
   6. **Generates Report** - Creates comprehensive terminal output with statistics
   7. **Saves Data** - Exports everything to `02-DiscordBot-Users_Stats-DataReport_Output.json` for future reference
   8. **Terminates** - Automatically exits when analysis is complete

## Sample Output

```
🚀 Starting Standalone Discord Analytics Admin Report Generator...

✅ Connected to Discord as YourBot#1234
📊 Bot is in 2 guild(s)

🔍 Starting comprehensive Discord analysis...

📋 Analyzing Server: My Server (ID: 123456789)
   Members: 45
   Text Channels: 6 accessible, 2 private/restricted
   🔍 Scanning #announcements...
   🔍 Scanning #general...
     ... 500 messages scanned, 234 reactions found
   🔍 Scanning #memes...
   🔍 Scanning #off-topic...
   ⚠️  Skipped 2 private/restricted channels:
      - #admin-only
      - #mod-chat

📊 Analysis Complete!
   Channels Scanned: 6
   Messages Analyzed: 2,847
   Reactions Found: 1,293

⚠️  Summary of Skipped Channels (2 total):
   - My Server#admin-only
   - My Server#mod-chat
   Reason: Private channels or insufficient permissions

💾 Analytics data saved to '02-DiscordBot-Users_Stats-DataReport_Output.json'

📊 DISCORD ANALYTICS - COMPREHENSIVE ADMIN REPORT
Generated: 2025-11-09 17:30:15

📈 SUMMARY STATISTICS
----------------------------------------
Total Users Tracked: 42
Total Channels: 8
Total Messages: 2,847
Total Reactions Given: 1,293
Total Reactions Received: 1,293
Average Reactions per Message: 0.45

🏆 TOP 10 LEADERBOARDS
----------------------------------------

💬 Top Message Senders:
   1. Alice                    287 messages
   2. Bob                      234 messages

👥 DETAILED USER STATISTICS (Alphabetical Order)

📊 Alice (ID: 123456789)
   💬 Messages: 287
   👍 Reactions Given: 145
   ⭐ Reactions Received: 423
   📝 Active in 6 channel(s)
   🎯 Top Emojis Given: 👍(67), ❤️(34), 😂(23)
   🏆 Top Emojis Received: 🎉(89), 👍(156), ❤️(78)
```

## Required Discord Settings

### **CRITICAL: Enable Privileged Gateway Intents**
In the Discord Developer Portal, go to your bot's "Bot" section and enable:
- ✅ **Message Content Intent** - Required for reading message content
- ✅ **Server Members Intent** - Required for accessing member information

**Without these, the script will fail with a "privileged intents" error.**

### **Bot Permissions Required**
The bot needs these permissions in each server:
- `Read Message History` - **Essential** for scanning historical messages
- `View Channel` - To see channels
- `Send Messages` - For basic functionality (though not used in standalone mode)

## Troubleshooting

### Script fails with "privileged intents" error
- Go to Discord Developer Portal → Your Bot → Bot section
- Enable "Message Content Intent" and "Server Members Intent"
- Save changes and try again

### "No permission to read" errors
- Make sure the bot has "Read Message History" permission
- Check that the bot role is high enough in the server's role hierarchy
- Verify the bot has access to the channels you want to analyze

### Bot token errors
- Verify the bot token is correct in your `.env` file
- Make sure you're using the bot token from the "Bot" section, not Application ID
- Try regenerating the bot token if needed

### No data found
- Ensure the bot has been invited to the servers you want to analyze
- Check that there are actually messages and reactions in the channels
- Verify the bot has permission to read the channels

## Files Created

After running the script, you'll have:
- `02-DiscordBot-Users_Stats-DataReport_Output.json` - Complete data export with all statistics
- Terminal output with comprehensive report

## Privacy & Security

- ✅ **Admin-Only Access** - Reports only appear in your terminal
- ✅ **No Discord Messages** - Nothing is posted to Discord channels
- ✅ **Local Data Storage** - All data stays on your computer
- ✅ **One-Time Execution** - Script runs once and terminates

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.
