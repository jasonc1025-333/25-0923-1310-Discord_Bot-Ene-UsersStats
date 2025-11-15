#!/usr/bin/env python3
"""
Standalone Discord Analytics Admin Report Generator
Connects to Discord, scans all channels, collects data, and generates a comprehensive terminal report.
This script does everything from start to end and makes other bot files obsolete.
"""

import discord
import json
import os
import asyncio
from collections import defaultdict
from datetime import datetime, timezone
from dotenv import load_dotenv

# Debug mode flag (will be set after loading environment variables)
DEBUG_MODE = False

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

class DiscordAnalyticsReporter:
    def __init__(self, token, start_date=None, end_date=None):
        self.client = discord.Client(intents=intents)
        self.token = token
        self.start_date = start_date
        self.end_date = end_date
        self.analytics_data = {
            'messages': defaultdict(lambda: defaultdict(int)),
            'reactions_given': defaultdict(lambda: defaultdict(lambda: defaultdict(int))),
            'reactions_received': defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        }
        self.user_names = {}  # Cache for user display names
        
        # Set up event handlers
        @self.client.event
        async def on_ready():
            print(f'✅ Connected to Discord as {self.client.user}')
            print(f'📊 Bot is in {len(self.client.guilds)} server_guild(s)')
            
            # Start the analysis process
            await self.analyze_all_server_guilds()
            
            # Generate and display the report
            self.generate_comprehensive_report()
            
            # Properly close discord.py's internal HTTP session before closing the client
            if hasattr(self.client, 'http') and hasattr(self.client.http, '_HTTPClient__session'):
                if self.client.http._HTTPClient__session is not None:
                    await self.client.http._HTTPClient__session.close()
            
            # Close the Discord client connection
            await self.client.close()
            
            # Give the event loop time to process any final cleanup tasks
            await asyncio.sleep(0.5)
    
    async def analyze_all_server_guilds(self):
        """Analyze all servers the bot has access to"""
        print("\n🔍 Starting comprehensive Discord analysis...")
        print("=" * 60)
        
        total_channels = 0
        total_messages_scanned = 0
        total_reactions_found = 0
        skipped_channels = []
        
        for server_guild in self.client.guilds:
            print(f"\n📋 Analyzing Server: {server_guild.name} (ID: {server_guild.id})")
            print(f"   Members: {server_guild.member_count:,}")
            
            # Cache member names for this server
            for member in server_guild.members:
                if not member.bot:
                    self.user_names[str(member.id)] = member.display_name
            
            # Get text channels sorted by position (visual order in Discord)
            text_channels = [channel for channel in server_guild.channels if isinstance(channel, discord.TextChannel)]
            text_channels.sort(key=lambda x: x.position)
            
            # Count private channels (channels we can't access)
            private_channels = []
            accessible_channels = []
            
            for channel in text_channels:
                try:
                    # Test if we can read the channel
                    permissions = channel.permissions_for(server_guild.me)
                    if permissions.read_message_history and permissions.view_channel:
                        accessible_channels.append(channel)
                    else:
                        private_channels.append(channel)
                except:
                    private_channels.append(channel)
            
            print(f"   Text Channels: {len(accessible_channels)} accessible, {len(private_channels)} private/restricted")
            
            # Process accessible channels in visual order
            for channel in accessible_channels:
                try:
                    print(f"   🔍 Scanning #{channel.name}...")
                    channel_messages, channel_reactions = await self.analyze_channel(channel)
                    total_messages_scanned += channel_messages
                    total_reactions_found += channel_reactions
                    total_channels += 1
                    
                except discord.Forbidden:
                    print(f"   ❌ No permission to read #{channel.name}")
                    skipped_channels.append(f"{server_guild.name}#{channel.name}")
                except Exception as e:
                    print(f"   ❌ Error scanning #{channel.name}: {str(e)}")
                    skipped_channels.append(f"{server_guild.name}#{channel.name}")
            
            # List private/restricted channels for this server
            if private_channels:
                print(f"   ⚠️  Skipped {len(private_channels)} private/restricted channels:")
                for channel in private_channels:
                    print(f"      - #{channel.name}")
                    skipped_channels.append(f"{server_guild.name}#{channel.name}")
        
        print(f"\n📊 Analysis Complete!")
        print(f"   Channels Scanned: {total_channels}")
        print(f"   Messages Analyzed: {total_messages_scanned:,}")
        print(f"   Reactions Found: {total_reactions_found:,}")
        
        # Summary of skipped channels
        if skipped_channels:
            print(f"\n⚠️  Summary of Skipped Channels ({len(skipped_channels)} total):")
            for channel_name in skipped_channels:
                print(f"   - {channel_name}")
            print("   Reason: Private channels or insufficient permissions")
        
        # Save data to JSON file
        self.save_analytics_data()
    
    async def analyze_channel(self, channel, limit=None):
        """Analyze a single channel for messages and reactions"""
        channel_id = str(channel.id)
        messages_count = 0
        reactions_count = 0
        messages_in_range = 0
        last_update_time = 0
        
        # Display date range info
        date_range_info = ""
        if self.start_date or self.end_date:
            if self.start_date and self.end_date:
                date_range_info = f" (Date range: {self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')})"
            elif self.start_date:
                date_range_info = f" (From: {self.start_date.strftime('%Y-%m-%d')})"
            elif self.end_date:
                date_range_info = f" (Until: {self.end_date.strftime('%Y-%m-%d')})"
        
        # Always scan ALL messages in the channel for complete historical data
        print(f"     🔍 Scanning ALL historical messages{date_range_info} (this may take a while)...")
        
        if DEBUG_MODE:
            print(f"🔍 DEBUG: Starting full historical scan for #{channel.name}")
            print(f"   Channel ID: {channel_id}")
            print(f"   Date range: {date_range_info if date_range_info else 'All time'}")
        
        # First, get an estimate of total messages for progress tracking
        try:
            # Quick estimate by checking recent messages
            recent_messages = []
            async for msg in channel.history(limit=100):
                recent_messages.append(msg)
            
            if len(recent_messages) < 100:
                estimated_total = len(recent_messages)
            else:
                # Estimate based on channel age and recent activity
                if recent_messages:
                    oldest_recent = recent_messages[-1].created_at
                    newest_recent = recent_messages[0].created_at
                    time_span = (newest_recent - oldest_recent).total_seconds()
                    if time_span > 0:
                        messages_per_second = 100 / time_span
                        channel_age = (newest_recent - channel.created_at).total_seconds()
                        estimated_total = min(int(messages_per_second * channel_age), 100000)  # Increased cap for full scan
                    else:
                        estimated_total = 1000  # Default estimate
                else:
                    estimated_total = 1000
        except:
            estimated_total = 1000  # Fallback estimate
        
        try:
            import time
            start_time = time.time()
            
            # Set up date filtering parameters for channel.history()
            history_kwargs = {}
            if limit is not None:
                history_kwargs['limit'] = limit
            if self.start_date:
                history_kwargs['after'] = self.start_date
            if self.end_date:
                history_kwargs['before'] = self.end_date
            
            if DEBUG_MODE:
                print(f"🔍 DEBUG: Starting message iteration with kwargs: {history_kwargs}")
            
            async for message in channel.history(**history_kwargs):
                messages_count += 1
                
                # Check if message is within date range (additional check for precision)
                message_in_range = True
                if self.start_date and message.created_at < self.start_date:
                    message_in_range = False
                if self.end_date and message.created_at > self.end_date:
                    message_in_range = False
                
                if message_in_range:
                    messages_in_range += 1
                    
                    # Track message count (skip bot messages)
                    if not message.author.bot:
                        user_id = str(message.author.id)
                        self.analytics_data['messages'][user_id][channel_id] += 1
                        
                        # Cache user name
                        if user_id not in self.user_names:
                            self.user_names[user_id] = message.author.display_name
                    
                    # Process reactions on this message
                    for reaction in message.reactions:
                        emoji = str(reaction.emoji)
                        message_author_id = str(message.author.id)
                        
                        # Get all users who reacted with this emoji
                        async for user in reaction.users():
                            if user.bot:
                                continue  # Skip bot reactions
                            
                            user_id = str(user.id)
                            reactions_count += 1
                            
                            # Cache user name
                            if user_id not in self.user_names:
                                self.user_names[user_id] = user.display_name
                            
                            # Track reactions given by user
                            self.analytics_data['reactions_given'][user_id][channel_id][emoji] += 1
                            
                            # Track reactions received by message author (don't count self-reactions)
                            if user_id != message_author_id:
                                self.analytics_data['reactions_received'][message_author_id][channel_id][emoji] += 1
                
                # Progress indicator every 10% increment or every 100 messages for large scans
                progress_percent = min(int((messages_count / estimated_total) * 100), 100)
                
                # For large scans, show progress more frequently
                if limit is None and messages_count % 100 == 0:
                    print(f"\r     📊 {progress_percent:3d}% | {messages_count:,} messages ({messages_in_range:,} in range), {reactions_count:,} reactions", end='', flush=True)
                # For smaller scans, show progress at 10% increments
                elif limit is not None and progress_percent > 0 and progress_percent % 10 == 0 and progress_percent != last_update_time:
                    print(f"\r     📊 {progress_percent:3d}% | {messages_count:,} messages ({messages_in_range:,} in range), {reactions_count:,} reactions", end='', flush=True)
                    last_update_time = progress_percent
                # Show progress between milestones to indicate activity
                elif messages_count % 5 == 0:
                    current_progress = min(int((messages_count / estimated_total) * 100), 100)
                    print(f"\r     📊 {current_progress:3d}% | {messages_count:,} messages ({messages_in_range:,} in range), {reactions_count:,} reactions", end='', flush=True)
        
        except Exception as e:
            print(f"\r     Error: {str(e)}")
        
        # Final status update with newline
        if messages_count > 0:
            progress_percent = min(int((messages_count / estimated_total) * 100), 100)
            if self.start_date or self.end_date:
                print(f"\r     ✅ {progress_percent:3d}% | {messages_count:,} messages ({messages_in_range:,} in range), {reactions_count:,} reactions")
            else:
                print(f"\r     ✅ {progress_percent:3d}% | {messages_count:,} messages, {reactions_count:,} reactions")
        
        return messages_in_range, reactions_count
    
    def save_analytics_data(self):
        """Save analytics data to JSON file"""
        # Convert defaultdicts to regular dicts for JSON serialization
        json_data = {
            'messages': {
                user_id: dict(channels) for user_id, channels in self.analytics_data['messages'].items()
            },
            'reactions_given': {
                user_id: {
                    channel_id: dict(emojis) for channel_id, emojis in channels.items()
                } for user_id, channels in self.analytics_data['reactions_given'].items()
            },
            'reactions_received': {
                user_id: {
                    channel_id: dict(emojis) for channel_id, emojis in channels.items()
                } for user_id, channels in self.analytics_data['reactions_received'].items()
            },
            'user_names': self.user_names,
            'generated_at': datetime.now().isoformat()
        }
        
        with open('02-DiscordBot-Users_Stats-DataReport_Output.json', 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Analytics data saved to '02-DiscordBot-Users_Stats-DataReport_Output.json'")
    
    def get_user_display_name(self, user_id):
        """Get display name for user ID"""
        return self.user_names.get(user_id, f"User-{user_id}")
    
    def generate_comprehensive_report(self):
        """Generate and print a comprehensive analytics report"""
        print("\n" + "="*80)
        print("📊 DISCORD ANALYTICS - COMPREHENSIVE ADMIN REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Collect all users and their total stats
        user_stats = {}
        all_channels = set()
        
        # Process messages
        for user_id, channels in self.analytics_data['messages'].items():
            if user_id not in user_stats:
                user_stats[user_id] = {
                    'display_name': self.get_user_display_name(user_id),
                    'total_messages': 0,
                    'total_reactions_given': 0,
                    'total_reactions_received': 0,
                    'channels': set(),
                    'top_emojis_given': defaultdict(int),
                    'top_emojis_received': defaultdict(int)
                }
            
            for channel_id, count in channels.items():
                user_stats[user_id]['total_messages'] += count
                user_stats[user_id]['channels'].add(channel_id)
                all_channels.add(channel_id)
        
        # Process reactions given
        for user_id, channels in self.analytics_data['reactions_given'].items():
            if user_id not in user_stats:
                user_stats[user_id] = {
                    'display_name': self.get_user_display_name(user_id),
                    'total_messages': 0,
                    'total_reactions_given': 0,
                    'total_reactions_received': 0,
                    'channels': set(),
                    'top_emojis_given': defaultdict(int),
                    'top_emojis_received': defaultdict(int)
                }
            
            for channel_id, emojis in channels.items():
                user_stats[user_id]['channels'].add(channel_id)
                all_channels.add(channel_id)
                for emoji, count in emojis.items():
                    user_stats[user_id]['total_reactions_given'] += count
                    user_stats[user_id]['top_emojis_given'][emoji] += count
        
        # Process reactions received
        for user_id, channels in self.analytics_data['reactions_received'].items():
            if user_id not in user_stats:
                user_stats[user_id] = {
                    'display_name': self.get_user_display_name(user_id),
                    'total_messages': 0,
                    'total_reactions_given': 0,
                    'total_reactions_received': 0,
                    'channels': set(),
                    'top_emojis_given': defaultdict(int),
                    'top_emojis_received': defaultdict(int)
                }
            
            for channel_id, emojis in channels.items():
                user_stats[user_id]['channels'].add(channel_id)
                all_channels.add(channel_id)
                for emoji, count in emojis.items():
                    user_stats[user_id]['total_reactions_received'] += count
                    user_stats[user_id]['top_emojis_received'][emoji] += count
        
        # Summary Statistics
        print("📈 SUMMARY STATISTICS")
        print("-" * 40)
        print(f"Total Users Tracked: {len(user_stats):,}")
        print(f"Total Channels: {len(all_channels):,}")
        
        total_messages = sum(stats['total_messages'] for stats in user_stats.values())
        total_reactions_given = sum(stats['total_reactions_given'] for stats in user_stats.values())
        total_reactions_received = sum(stats['total_reactions_received'] for stats in user_stats.values())
        
        print(f"Total Messages: {total_messages:,}")
        print(f"Total Reactions Given: {total_reactions_given:,}")
        print(f"Total Reactions Received: {total_reactions_received:,}")
        
        if total_messages > 0:
            avg_reactions_per_message = total_reactions_received / total_messages
            print(f"Average Reactions per Message: {avg_reactions_per_message:.2f}")
        
        print()
        
        # Complete User Leaderboards
        print("🏆 COMPLETE USER LEADERBOARDS")
        print("-" * 40)
        
        # Top by messages (all users with messages)
        top_messages = sorted(user_stats.items(), key=lambda x: x[1]['total_messages'], reverse=True)
        users_with_messages = [item for item in top_messages if item[1]['total_messages'] > 0]
        print(f"\n💬 Message Senders Leaderboard ({len(users_with_messages)} users):")
        for i, (user_id, stats) in enumerate(users_with_messages, 1):
            print(f"  {i:2d}. {stats['display_name']:<25} {stats['total_messages']:,} messages")
        
        # Top by reactions given (all users with reactions given)
        top_reactions_given = sorted(user_stats.items(), key=lambda x: x[1]['total_reactions_given'], reverse=True)
        users_with_reactions_given = [item for item in top_reactions_given if item[1]['total_reactions_given'] > 0]
        print(f"\n👍 Reaction Givers Leaderboard ({len(users_with_reactions_given)} users):")
        for i, (user_id, stats) in enumerate(users_with_reactions_given, 1):
            print(f"  {i:2d}. {stats['display_name']:<25} {stats['total_reactions_given']:,} reactions given")
        
        # Top by reactions received (all users with reactions received)
        top_reactions_received = sorted(user_stats.items(), key=lambda x: x[1]['total_reactions_received'], reverse=True)
        users_with_reactions_received = [item for item in top_reactions_received if item[1]['total_reactions_received'] > 0]
        print(f"\n⭐ Reaction Receivers Leaderboard ({len(users_with_reactions_received)} users):")
        for i, (user_id, stats) in enumerate(users_with_reactions_received, 1):
            print(f"  {i:2d}. {stats['display_name']:<25} {stats['total_reactions_received']:,} reactions received")
        
        print()
        
        # Detailed User Report (Alphabetical)
        print("👥 DETAILED USER STATISTICS (Alphabetical Order)")
        print("=" * 80)
        
        # Sort users alphabetically by display name
        sorted_users = sorted(user_stats.items(), key=lambda x: x[1]['display_name'].lower())
        
        for user_id, stats in sorted_users:
            print(f"\n📊 {stats['display_name']} (ID: {user_id})")
            print(f"   💬 Messages: {stats['total_messages']:,}")
            print(f"   👍 Reactions Given: {stats['total_reactions_given']:,}")
            print(f"   ⭐ Reactions Received: {stats['total_reactions_received']:,}")
            print(f"   📝 Active in {len(stats['channels'])} channel(s)")
            
            # Top emojis given
            if stats['top_emojis_given']:
                top_given = sorted(stats['top_emojis_given'].items(), key=lambda x: x[1], reverse=True)[:5]
                emoji_list = ", ".join([f"{emoji}({count})" for emoji, count in top_given])
                print(f"   🎯 Top Emojis Given: {emoji_list}")
            
            # Top emojis received
            if stats['top_emojis_received']:
                top_received = sorted(stats['top_emojis_received'].items(), key=lambda x: x[1], reverse=True)[:5]
                emoji_list = ", ".join([f"{emoji}({count})" for emoji, count in top_received])
                print(f"   🏆 Top Emojis Received: {emoji_list}")
        
        print()
        print("=" * 80)
        print("📊 Report Complete!")
        print("=" * 80)
    
    async def run(self):
        """Run the Discord client"""
        await self.client.start(self.token)

def parse_date(date_str):
    """Parse date string in YYYY-MM-DD format and make it timezone-aware (UTC)"""
    try:
        # Parse the date and make it timezone-aware (UTC) to match Discord timestamps
        naive_date = datetime.strptime(date_str, '%Y-%m-%d')
        return naive_date.replace(tzinfo=timezone.utc)
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD format.")

def main():
    """Main function"""
    import sys
    
    print("🚀 Starting Standalone Discord Analytics Admin Report Generator...")
    print(f"🐍 Python Version: {sys.version.split()[0]}")
    
    # Parse command line arguments for date range
    start_date = None
    end_date = None
    
    if len(sys.argv) > 1:
        print("\n📅 Date Range Parameters:")
        for i, arg in enumerate(sys.argv[1:], 1):
            if arg.startswith('--start=') or arg.startswith('-s='):
                date_str = arg.split('=', 1)[1]
                try:
                    start_date = parse_date(date_str)
                    print(f"   Start Date: {start_date.strftime('%Y-%m-%d')}")
                except ValueError as e:
                    print(f"❌ Error: {e}")
                    return
            elif arg.startswith('--end=') or arg.startswith('-e='):
                date_str = arg.split('=', 1)[1]
                try:
                    end_date = parse_date(date_str)
                    print(f"   End Date: {end_date.strftime('%Y-%m-%d')}")
                except ValueError as e:
                    print(f"❌ Error: {e}")
                    return
            elif arg in ['--help', '-h']:
                print("\n📋 Usage:")
                print("  python 01-DiscordBot-Users_Stats-RunMe-ForAdminExternalConsole.py [options]")
                print("\n🔧 Options:")
                print("  --start=YYYY-MM-DD, -s=YYYY-MM-DD    Start date for analysis")
                print("  --end=YYYY-MM-DD, -e=YYYY-MM-DD      End date for analysis")
                print("  --help, -h                           Show this help message")
                print("\n📝 Examples:")
                print("  # Analyze all messages from 2024-01-01 onwards:")
                print("  python 01-DiscordBot-Users_Stats-RunMe-ForAdminExternalConsole.py --start=2024-01-01")
                print("\n  # Analyze messages from January 2024:")
                print("  python 01-DiscordBot-Users_Stats-RunMe-ForAdminExternalConsole.py --start=2024-01-01 --end=2024-01-31")
                print("\n  # Analyze messages until December 2023:")
                print("  python 01-DiscordBot-Users_Stats-RunMe-ForAdminExternalConsole.py --end=2023-12-31")
                return
            else:
                print(f"❌ Unknown argument: {arg}")
                print("Use --help for usage information.")
                return
    
    # Validate date range
    if start_date and end_date and start_date > end_date:
        print("❌ Error: Start date must be before end date.")
        return
    
    print()
    
    # Load environment variables from custom .env file
    load_dotenv('.env-SecretDiscordBotToken-NotPublishToGithub')
    
    # Set DEBUG_MODE after loading environment variables
    global DEBUG_MODE
    debug_env_value = os.getenv('DEBUG_MODE', 'NOT_SET')
    DEBUG_MODE = debug_env_value.lower() == 'true'
    
    # ALWAYS print DEBUG_MODE status at startup for troubleshooting
    print(f"🔧 DEBUG_MODE Environment Variable: '{debug_env_value}'")
    print(f"🔧 DEBUG_MODE Evaluated As: {DEBUG_MODE}")
    if DEBUG_MODE:
        print("✅ DEBUG MODE IS ENABLED - You should see detailed debug output")
    else:
        print("❌ DEBUG MODE IS DISABLED - Set DEBUG_MODE=true to enable debug output")
    print("="*60)
    print()
    
    # Get the bot token
    token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not token:
        print("❌ Error: DISCORD_BOT_TOKEN not found!")
        print("\n📋 Setup Instructions:")
        print("1. Copy .env.example to .env")
        print("2. Edit .env and add your Discord bot token")
        print("3. Run this script again")
        print("\n🔗 Get a bot token at: https://discord.com/developers/applications")
        return
    
    try:
        # Create and run the reporter with date range
        reporter = DiscordAnalyticsReporter(token, start_date, end_date)
        asyncio.run(reporter.run())
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        print("\n🔧 Common solutions:")
        print("- Check that your bot token is correct")
        print("- Ensure the bot has proper permissions")
        print("- Make sure discord.py is installed: pip install -r requirements.txt")
        print("- Enable privileged intents in Discord Developer Portal")
        print("\n💡 Note: If you see 'Session is closed' error:")
        print("- This is a harmless cleanup timing issue that can be safely ignored")
        print("- All data collection, report generation, and JSON saving completed successfully")
        print("- The error only occurs during final HTTP session cleanup")
    
    print("\n✅ Standalone admin report script completed.")

if __name__ == "__main__":
    main()
