import discord
from discord.ext import commands
import json
import os
import sys
import logging
from datetime import datetime, timezone
from collections import defaultdict
import asyncio

# Debug mode flag (will be set after loading environment variables)
DEBUG_MODE = False

# Set up logging for local development
def setup_logging():
    """Set up logging for local development"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # For local development: Use multiple handlers
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/discord_bot.log', encoding='utf-8')
        ],
        force=True  # Override any existing configuration
    )
    
    # Ensure immediate flushing
    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.StreamHandler):
            handler.stream.reconfigure(line_buffering=True)
    
    return logging.getLogger(__name__)

# Initialize logger
logger = setup_logging()


# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

# Create bot with explicit shard configuration to prevent double connections
bot = commands.Bot(
    command_prefix='!', 
    intents=intents,
    max_messages=1000,  # Limit message cache
    chunk_guilds_at_startup=False  # Don't auto-chunk guilds
)

# Data storage
DATA_FILE = '12-DiscordBot-Users_Stats-DataReport_Output.json'

def load_data():
    """Load analytics data from JSON file"""
    if os.path.exists(DATA_FILE):
        if DEBUG_MODE:
            print(f"🔍 DEBUG: Loading existing data from {DATA_FILE}")
        
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if DEBUG_MODE:
            print(f"   📊 Raw data loaded:")
            print(f"     Messages: {len(data.get('messages', {}))} users")
            print(f"     Reactions Given: {len(data.get('reactions_given', {}))} users")
            print(f"     Reactions Received: {len(data.get('reactions_received', {}))} users")
        
        # Convert loaded data back to defaultdicts
        converted_data = {
            'messages': defaultdict(lambda: defaultdict(int), {
                user_id: defaultdict(int, channels) 
                for user_id, channels in data.get('messages', {}).items()
            }),
            'reactions_given': defaultdict(lambda: defaultdict(lambda: defaultdict(int)), {
                user_id: defaultdict(lambda: defaultdict(int), {
                    channel_id: defaultdict(int, emojis)
                    for channel_id, emojis in channels.items()
                })
                for user_id, channels in data.get('reactions_given', {}).items()
            }),
            'reactions_received': defaultdict(lambda: defaultdict(lambda: defaultdict(int)), {
                user_id: defaultdict(lambda: defaultdict(int), {
                    channel_id: defaultdict(int, emojis)
                    for channel_id, emojis in channels.items()
                })
                for user_id, channels in data.get('reactions_received', {}).items()
            })
        }
        
        if DEBUG_MODE:
            print(f"   ✅ Data converted to defaultdicts successfully")
        
        return converted_data
    else:
        if DEBUG_MODE:
            print(f"🔍 DEBUG: No existing data file found ({DATA_FILE}), creating new data structure")
        
        return {
            'messages': defaultdict(lambda: defaultdict(int)),  # user_id -> channel_id -> count
            'reactions_given': defaultdict(lambda: defaultdict(lambda: defaultdict(int))),  # user_id -> channel_id -> emoji -> count
            'reactions_received': defaultdict(lambda: defaultdict(lambda: defaultdict(int)))  # user_id -> channel_id -> emoji -> count
        }

def save_data(data):
    """Save analytics data to JSON file"""
    if DEBUG_MODE:
        print(f"🔍 DEBUG: Saving data to {DATA_FILE}")
        print(f"   📊 Current data counts:")
        print(f"     Messages: {len(data['messages'])} users")
        print(f"     Reactions Given: {len(data['reactions_given'])} users")
        print(f"     Reactions Received: {len(data['reactions_received'])} users")
    
    # Convert defaultdicts to regular dicts for JSON serialization
    json_data = {
        'messages': dict(data['messages']),
        'reactions_given': dict(data['reactions_given']),
        'reactions_received': dict(data['reactions_received'])
    }
    
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        if DEBUG_MODE:
            print(f"   ✅ Data saved successfully")
    except Exception as e:
        if DEBUG_MODE:
            print(f"   ❌ Error saving data: {e}")
        else:
            print(f"❌ Error saving analytics data: {e}")

def parse_date(date_str):
    """Parse date string in YYYY-MM-DD format and make it timezone-aware (UTC)"""
    try:
        # Parse the date and make it timezone-aware (UTC) to match Discord timestamps
        naive_date = datetime.strptime(date_str, '%Y-%m-%d')
        return naive_date.replace(tzinfo=timezone.utc)
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD format.")

async def ensure_reaction_data(ctx, progress_increment=10, scan_message="🔍 **No reaction data found. Scanning recent message history...**"):
    """
    Check if reaction data exists for the current channel, and if not, scan historical messages.
    
    Args:
        ctx: Discord command context
        progress_increment: How often to show progress updates (10 = every 10%, 20 = every 20%)
        scan_message: Custom message to show when starting scan
    
    Returns:
        bool: True if data exists or was successfully scanned, False if error occurred
    """
    channel_id = str(ctx.channel.id)
    
    # Check if we have any reaction data for this channel
    has_reaction_data = False
    for user_data in analytics_data['reactions_given'].values():
        if channel_id in user_data and any(user_data[channel_id].values()):
            has_reaction_data = True
            break
    
    if not has_reaction_data:
        for user_data in analytics_data['reactions_received'].values():
            if channel_id in user_data and any(user_data[channel_id].values()):
                has_reaction_data = True
                break
    
    # If no reaction data exists, automatically scan recent history
    if not has_reaction_data:
        status_msg = await ctx.send(scan_message)
        
        try:
            messages_scanned = 0
            reactions_found = 0
            limit = 1000  # Scan last 1000 messages
            last_update_percent = 0
            
            async for message in ctx.channel.history(limit=limit):
                messages_scanned += 1
                
                # Process reactions on this message
                for reaction in message.reactions:
                    emoji = str(reaction.emoji)
                    message_author_id = str(message.author.id)
                    
                    # Get all users who reacted with this emoji
                    async for user in reaction.users():
                        if user.bot:
                            continue  # Skip bot reactions
                        
                        user_id = str(user.id)
                        reactions_found += 1
                        
                        # Track reactions given by user
                        analytics_data['reactions_given'][user_id][channel_id][emoji] += 1
                        
                        # Track reactions received by message author (don't count self-reactions)
                        if user_id != message_author_id:
                            analytics_data['reactions_received'][message_author_id][channel_id][emoji] += 1
                
                # Update progress with percentage
                progress_percent = min(int((messages_scanned / limit) * 100), 100)
                
                # Show progress at specified increments
                if progress_percent > 0 and progress_percent % progress_increment == 0 and progress_percent != last_update_percent:
                    try:
                        await status_msg.edit(content=f"🔍 **Scanning history...** 📊 {progress_percent:3d}% | {messages_scanned:,} messages, {reactions_found:,} reactions")
                        last_update_percent = progress_percent
                    except:
                        pass  # Ignore edit errors
                # Show progress every 50 messages to indicate activity
                elif messages_scanned % 50 == 0:
                    try:
                        current_progress = min(int((messages_scanned / limit) * 100), 100)
                        await status_msg.edit(content=f"🔍 **Scanning history...** 📊 {current_progress:3d}% | {messages_scanned:,} messages, {reactions_found:,} reactions")
                    except:
                        pass  # Ignore edit errors
            
            # Save the updated data
            save_data(analytics_data)
            
            # Final status with completion
            final_percent = min(int((messages_scanned / limit) * 100), 100)
            await status_msg.edit(content=f"✅ **Historical scan complete!** 📊 {final_percent:3d}% | {messages_scanned:,} messages, {reactions_found:,} reactions")
            
            return True
            
        except Exception as e:
            await status_msg.edit(content=f"❌ Error scanning history: {str(e)}")
            return False
    
    return True  # Data already exists

# Load data on startup
analytics_data = load_data()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} server_guilds')
    
    if DEBUG_MODE:
        print(f"\n🔍 DEBUG: Bot startup complete")
        print(f"   Bot User ID: {bot.user.id}")
        print(f"   Bot Username: {bot.user.name}")
        print(f"   Bot Display Name: {bot.user.display_name}")
        print(f"   Guilds connected to:")
        for guild in bot.guilds:
            print(f"     - {guild.name} (ID: {guild.id}, Members: {guild.member_count})")
        print(f"   Data file: {DATA_FILE}")
        print(f"   Existing data loaded: {len(analytics_data['messages'])} users with messages, {len(analytics_data['reactions_given'])} users with reactions given")
        print("="*60)

@bot.event
async def on_message(message):
    # Don't count bot messages
    if message.author.bot:
        if DEBUG_MODE:
            is_self = message.author.id == bot.user.id
            bot_type = "THIS BOT (self)" if is_self else "OTHER BOT"
            print(f"🔍 DEBUG: Ignoring bot message from {message.author.name} [{bot_type}]")
            print(f"   ℹ️  Reason: Bot messages are excluded from analytics to track only human user activity")
            print(f"   🤖 Bot ID: {message.author.id}")
            if message.content:
                print(f"   💬 Message content: {message.content[:50]}{'...' if len(message.content) > 50 else ''}")
            elif message.embeds:
                print(f"   📊 Message type: Embed message (no text content)")
            else:
                print(f"   💬 Message type: Empty or system message")
        return
    
    user_id = str(message.author.id)
    channel_id = str(message.channel.id)
    
    # Debug logging for all messages (not just commands)
    if DEBUG_MODE:
        print(f"\n🔍 DEBUG: Message received")
        print(f"   👤 User: {message.author.name} (ID: {user_id})")
        print(f"   📝 Channel: #{message.channel.name} (ID: {channel_id})")
        print(f"   💬 Content: {message.content[:100]}{'...' if len(message.content) > 100 else ''}")
        print(f"   🕐 Timestamp: {message.created_at}")
        
        # Show current message count before increment
        current_count = analytics_data['messages'].get(user_id, {}).get(channel_id, 0)
        print(f"   📊 Current message count for user in this channel: {current_count}")
    
    # Debug logging for commands
    if DEBUG_MODE and message.content.startswith('!'):
        print(f"   🤖 This is a command!")
        print(f"   Current total users tracked: {len(analytics_data['messages'])}")
    
    # Track message count
    if user_id not in analytics_data['messages']:
        analytics_data['messages'][user_id] = defaultdict(int)
        if DEBUG_MODE:
            print(f"   ➕ New user added to message tracking: {user_id}")
    
    old_count = analytics_data['messages'][user_id][channel_id]
    analytics_data['messages'][user_id][channel_id] += 1
    new_count = analytics_data['messages'][user_id][channel_id]
    
    if DEBUG_MODE:
        print(f"   📈 Message count updated: {old_count} → {new_count}")
    
    save_data(analytics_data)
    
    # Process commands
    await bot.process_commands(message)

@bot.event
async def on_reaction_add(reaction, user):
    # Don't count bot reactions
    if user.bot:
        if DEBUG_MODE:
            print(f"🔍 DEBUG: Ignoring bot REACTION from {user.name}")
            print(f"   ℹ️  Reason: Bot reactions are excluded from analytics to track only human user activity")
            print(f"   🤖 Bot ID: {user.id}")
            print(f"   😀 Emoji: {reaction.emoji}")
        return
    
    user_id = str(user.id)
    channel_id = str(reaction.message.channel.id)
    emoji = str(reaction.emoji)
    message_author_id = str(reaction.message.author.id)
    
    # Debug logging
    if DEBUG_MODE:
        print(f"\n🔍 DEBUG: Reaction Event Triggered!")
        print(f"   👤 User: {user.name} (ID: {user_id})")
        print(f"   📝 Channel: #{reaction.message.channel.name} (ID: {channel_id})")
        print(f"   😀 Emoji: {emoji}")
        print(f"   📨 Message Author: {reaction.message.author.name} (ID: {message_author_id})")
        
        print(f"\n📊 BEFORE - Analytics Data:")
        print(f"   reactions_given keys: {list(analytics_data['reactions_given'].keys())}")
        print(f"   reactions_received keys: {list(analytics_data['reactions_received'].keys())}")
        
        if user_id in analytics_data['reactions_given']:
            print(f"   User {user_id} reactions_given: {dict(analytics_data['reactions_given'][user_id])}")
        else:
            print(f"   User {user_id} not in reactions_given yet")
            
        if message_author_id in analytics_data['reactions_received']:
            print(f"   Author {message_author_id} reactions_received: {dict(analytics_data['reactions_received'][message_author_id])}")
        else:
            print(f"   Author {message_author_id} not in reactions_received yet")
    
    # Track reactions given by user
    if user_id not in analytics_data['reactions_given']:
        analytics_data['reactions_given'][user_id] = defaultdict(lambda: defaultdict(int))
    analytics_data['reactions_given'][user_id][channel_id][emoji] += 1
    
    # Track reactions received by message author
    if message_author_id not in analytics_data['reactions_received']:
        analytics_data['reactions_received'][message_author_id] = defaultdict(lambda: defaultdict(int))
    analytics_data['reactions_received'][message_author_id][channel_id][emoji] += 1
    
    save_data(analytics_data)
    
    # Debug logging after
    if DEBUG_MODE:
        print(f"\n📊 AFTER - Analytics Data:")
        if user_id in analytics_data['reactions_given']:
            print(f"   User {user_id} reactions_given: {dict(analytics_data['reactions_given'][user_id])}")
        else:
            print(f"   ❌ User {user_id} STILL not in reactions_given!")
            
        if message_author_id in analytics_data['reactions_received']:
            print(f"   Author {message_author_id} reactions_received: {dict(analytics_data['reactions_received'][message_author_id])}")
        else:
            print(f"   ❌ Author {message_author_id} STILL not in reactions_received!")
        
        print(f"   📁 Data saved to file")
        print("="*50)

@bot.event
async def on_reaction_remove(reaction, user):
    # Don't count bot reactions
    if user.bot:
        return
    
    user_id = str(user.id)
    channel_id = str(reaction.message.channel.id)
    emoji = str(reaction.emoji)
    message_author_id = str(reaction.message.author.id)
    
    # Remove from reactions given
    if (user_id in analytics_data['reactions_given'] and 
        channel_id in analytics_data['reactions_given'][user_id] and
        emoji in analytics_data['reactions_given'][user_id][channel_id]):
        analytics_data['reactions_given'][user_id][channel_id][emoji] -= 1
        if analytics_data['reactions_given'][user_id][channel_id][emoji] <= 0:
            del analytics_data['reactions_given'][user_id][channel_id][emoji]
    
    # Remove from reactions received
    if (message_author_id in analytics_data['reactions_received'] and 
        channel_id in analytics_data['reactions_received'][message_author_id] and
        emoji in analytics_data['reactions_received'][message_author_id][channel_id]):
        analytics_data['reactions_received'][message_author_id][channel_id][emoji] -= 1
        if analytics_data['reactions_received'][message_author_id][channel_id][emoji] <= 0:
            del analytics_data['reactions_received'][message_author_id][channel_id][emoji]
    
    save_data(analytics_data)

@bot.command(name='stats_user')
async def user_stats(ctx, member: discord.Member = None):
    """Show statistics for a user (or yourself if no user specified)"""
    if member is None:
        member = ctx.author
    
    user_id = str(member.id)
    channel_id = str(ctx.channel.id)
    
    # Ensure reaction data exists, scan if needed
    scan_success = await ensure_reaction_data(
        ctx, 
        progress_increment=20, 
        scan_message="🔍 **No reaction data found. Scanning recent message history for complete user statistics...**"
    )
    
    if not scan_success:
        return  # Error occurred during scanning
    
    # Get message count
    message_count = analytics_data['messages'].get(user_id, {}).get(channel_id, 0)
    
    # Get reactions given
    reactions_given = analytics_data['reactions_given'].get(user_id, {}).get(channel_id, {})
    total_reactions_given = sum(reactions_given.values())
    
    # Get reactions received
    reactions_received = analytics_data['reactions_received'].get(user_id, {}).get(channel_id, {})
    total_reactions_received = sum(reactions_received.values())
    
    embed = discord.Embed(
        title=f"📊 Analytics for {member.display_name}",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(
        name="💬 Messages Posted",
        value=f"{message_count:,}",
        inline=True
    )
    
    embed.add_field(
        name="👍 Reactions Given",
        value=f"{total_reactions_given:,}",
        inline=True
    )
    
    embed.add_field(
        name="⭐ Reactions Received",
        value=f"{total_reactions_received:,}",
        inline=True
    )
    
    # Show top reactions given
    if reactions_given:
        top_given = sorted(reactions_given.items(), key=lambda x: x[1], reverse=True)[:5]
        given_text = "\n".join([f"{emoji}: {count}" for emoji, count in top_given])
        embed.add_field(
            name="🎯 Top Reactions Given",
            value=given_text,
            inline=True
        )
    
    # Show top reactions received
    if reactions_received:
        top_received = sorted(reactions_received.items(), key=lambda x: x[1], reverse=True)[:5]
        received_text = "\n".join([f"{emoji}: {count}" for emoji, count in top_received])
        embed.add_field(
            name="🏆 Top Reactions Received",
            value=received_text,
            inline=True
        )
    
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.set_footer(text=f"Channel: #{ctx.channel.name}")
    
    await ctx.send(embed=embed)

@bot.command(name='stats')
async def stats_leaderboard(ctx, percentage: int = 50):
    """Show leaderboards for all categories: messages, reactions given, and reactions received
    
    Args:
        percentage: Percentage of top users to show (default: 50%, range: 1-100%)
    """
    channel_id = str(ctx.channel.id)
    
    # Validate percentage parameter
    if percentage < 1 or percentage > 100:
        await ctx.send("❌ Percentage must be between 1 and 100!")
        return
    
    # Ensure reaction data exists, scan if needed
    scan_success = await ensure_reaction_data(
        ctx, 
        progress_increment=10, 
        scan_message="🔍 **No reaction data found. Scanning recent message history for complete statistics...**"
    )
    
    if not scan_success:
        return  # Error occurred during scanning
    
    # Collect data for all categories
    categories = {
        'messages': {},
        'reactions_given': {},
        'reactions_received': {}
    }
    
    # Get messages data
    for user_id, channels in analytics_data['messages'].items():
        if channel_id in channels:
            categories['messages'][user_id] = channels[channel_id]
    
    # Get reactions given data
    for user_id, channels in analytics_data['reactions_given'].items():
        if channel_id in channels:
            categories['reactions_given'][user_id] = sum(channels[channel_id].values())
    
    # Get reactions received data
    for user_id, channels in analytics_data['reactions_received'].items():
        if channel_id in channels:
            categories['reactions_received'][user_id] = sum(channels[channel_id].values())
    
    # Check if we have any data after scanning
    if not any(categories.values()):
        await ctx.send("📊 No data available for this channel yet! Try posting some messages and adding reactions.")
        return
    
    # Get all unique users across all categories
    all_users = set()
    for category_data in categories.values():
        all_users.update(category_data.keys())
    
    # Calculate how many users to show based on percentage
    total_users = len(all_users)
    users_to_show = max(1, int(total_users * percentage / 100))
    
    embed = discord.Embed(
        title=f"🏆 Channel Leaderboard (Top {percentage}%)",
        color=discord.Color.gold(),
        timestamp=datetime.utcnow()
    )
    
    # Helper function to format leaderboard
    def format_leaderboard(user_scores, limit):
        if not user_scores:
            return "No data available"
        
        sorted_users = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)[:limit]
        leaderboard_text = ""
        
        for i, (user_id, score) in enumerate(sorted_users, 1):
            try:
                user = bot.get_user(int(user_id))
                username = user.display_name if user else f"User {user_id}"
            except:
                username = f"User {user_id}"
            
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            leaderboard_text += f"{medal} **{username}**: {score:,}\n"
        
        return leaderboard_text
    
    # Add each category as a field
    embed.add_field(
        name="💬 Messages Posted",
        value=format_leaderboard(categories['messages'], users_to_show),
        inline=True
    )
    
    embed.add_field(
        name="👍 Reactions Given",
        value=format_leaderboard(categories['reactions_given'], users_to_show),
        inline=True
    )
    
    embed.add_field(
        name="⭐ Reactions Received",
        value=format_leaderboard(categories['reactions_received'], users_to_show),
        inline=True
    )
    
    # Add usage help
    embed.add_field(
        name="💡 Usage Examples",
        value="""
        `!stats` - Top 50% (default)
        `!stats 25` - Top 25%
        `!stats 100` - All users
        """,
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ Need Help?",
        value="Use `!stats_help` for all available commands and detailed documentation!",
        inline=False
    )
    
    embed.set_footer(text=f"Channel: #{ctx.channel.name} • Top {users_to_show} of {total_users} users ({percentage}%)")
    
    await ctx.send(embed=embed)

@bot.command(name='stats_mini')
async def stats_mini(ctx):
    """Show overall statistics for the current channel"""
    if DEBUG_MODE:
        print(f"\n🔍 DEBUG: stats_mini command STARTED")
        print(f"   👤 User: {ctx.author.name}")
        print(f"   📝 Channel: #{ctx.channel.name}")
    
    channel_id = str(ctx.channel.id)
    
    # Ensure reaction data exists, scan if needed
    scan_success = await ensure_reaction_data(
        ctx, 
        progress_increment=10, 
        scan_message="🔍 **No reaction data found. Scanning recent message history...**"
    )
    
    if not scan_success:
        return  # Error occurred during scanning
    
    total_messages = 0
    total_reactions_given = 0
    total_reactions_received = 0
    active_users = set()
    
    # Count messages
    for user_id, channels in analytics_data['messages'].items():
        if channel_id in channels:
            total_messages += channels[channel_id]
            active_users.add(user_id)
    
    # Count reactions given
    for user_id, channels in analytics_data['reactions_given'].items():
        if channel_id in channels:
            total_reactions_given += sum(channels[channel_id].values())
            active_users.add(user_id)
    
    # Count reactions received
    for user_id, channels in analytics_data['reactions_received'].items():
        if channel_id in channels:
            total_reactions_received += sum(channels[channel_id].values())
            active_users.add(user_id)
    
    embed = discord.Embed(
        title="📈 Channel Statistics\n📅 All-Time Analytics",
        color=discord.Color.green(),
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(name="💬 Total Messages", value=f"{total_messages:,}", inline=True)
    embed.add_field(name="👍 Total Reactions Given", value=f"{total_reactions_given:,}", inline=True)
    embed.add_field(name="⭐ Total Reactions Received", value=f"{total_reactions_received:,}", inline=True)
    embed.add_field(name="👥 Active Users", value=f"{len(active_users):,}", inline=True)
    
    if total_messages > 0:
        avg_reactions_per_message = total_reactions_received / total_messages
        embed.add_field(name="📊 Avg Reactions/Message", value=f"{avg_reactions_per_message:.2f}", inline=True)
    
    # Add note about date range analytics
    embed.add_field(
        name="📅 Date Range Analytics",
        value="**For date-specific analytics**, use the Admin Console script:\n`01-DiscordBot-Users_Stats-RunMe-ForAdminExternalConsole.py`",
        inline=False
    )
    
    
    embed.set_footer(text=f"Channel: #{ctx.channel.name}")
    
    if DEBUG_MODE:
        print(f"🔍 DEBUG: About to send stats_mini embed response")
        print(f"   📊 Total messages: {total_messages}")
        print(f"   👥 Active users: {len(active_users)}")
    
    await ctx.send(embed=embed)
    
    if DEBUG_MODE:
        print(f"🔍 DEBUG: stats_mini embed response SENT successfully")
        print(f"   ✅ stats_mini command COMPLETED")


@bot.command(name='stats_help')
async def stats_help(ctx):
    """Show help for analytics commands"""
    embed = discord.Embed(
        title="🤖 Discord Analytics Bot Help",
        color=discord.Color.purple(),
        description="Track and analyze user activity in your Discord channels!"
    )
    
    embed.add_field(
        name="📊 Discord Bot Commands",
        value="""
        `!stats_user [@user]` - Show stats for yourself or mentioned user
        `!stats_mini` - Show channel statistics (all-time)
        `!stats [percentage]` - Show top users ranking (default: top 50%)
        `!stats_help` - Show this help message
        """,
        inline=False
    )
    
    embed.add_field(
        name="🏆 Leaderboard Examples",
        value="""
        `!stats` - Show top 50% of users (default)
        `!stats 25` - Show top 25% of users
        `!stats 75` - Show top 75% of users
        `!stats 100` - Show all users
        """,
        inline=False
    )
    
    embed.add_field(
        name="📅 Date Range Analytics",
        value="""
        **For date-specific analytics**, use the Admin Console script:
        `01-DiscordBot-Users_Stats-RunMe-ForAdminExternalConsole.py`
        
        Examples:
        `python script.py --start=2024-01-01`
        `python script.py --start=2024-01-01 --end=2024-12-31`
        """,
        inline=False
    )
    
    embed.add_field(
        name="📈 What's Tracked",
        value="""
        • Messages posted per channel
        • Emoji reactions given by each user
        • Emoji reactions received by each user
        • Real-time tracking of reaction additions/removals
        • Automatic historical data scanning
        """,
        inline=False
    )
    
    embed.add_field(
        name="🔧 Discord Bot Features",
        value="""
        • Per-channel analytics
        • All-time statistics tracking
        • Top emoji usage tracking
        • Leaderboards and rankings
        • Beautiful embed displays
        • Smart historical data capture
        """,
        inline=False
    )
    
    embed.add_field(
        name="🚀 Smart Scanning",
        value="""
        This command automatically scans recent message history 
        if no reaction data exists, ensuring you always get meaningful statistics!
        """,
        inline=False
    )
    
    await ctx.send(embed=embed)

# Debug commands (only available when DEBUG_MODE is enabled)
@bot.command(name='debug_data')
async def debug_data(ctx):
    """Show current analytics data structure (Debug mode only)"""
    if not DEBUG_MODE:
        await ctx.send("❌ Debug commands are only available when DEBUG_MODE is enabled.")
        return
        
    embed = discord.Embed(title="🔍 Debug: Current Data Structure", color=discord.Color.orange())
    
    # Messages data
    msg_count = len(analytics_data['messages'])
    embed.add_field(name="💬 Messages", value=f"{msg_count} users tracked", inline=True)
    
    # Reactions given data
    given_count = len(analytics_data['reactions_given'])
    embed.add_field(name="👍 Reactions Given", value=f"{given_count} users tracked", inline=True)
    
    # Reactions received data
    received_count = len(analytics_data['reactions_received'])
    embed.add_field(name="⭐ Reactions Received", value=f"{received_count} users tracked", inline=True)
    
    # Show some sample data
    if analytics_data['reactions_given']:
        sample_user = list(analytics_data['reactions_given'].keys())[0]
        sample_data = dict(analytics_data['reactions_given'][sample_user])
        embed.add_field(name="📝 Sample Reactions Given", value=f"User {sample_user}: {sample_data}", inline=False)
    
    if analytics_data['reactions_received']:
        sample_user = list(analytics_data['reactions_received'].keys())[0]
        sample_data = dict(analytics_data['reactions_received'][sample_user])
        embed.add_field(name="📝 Sample Reactions Received", value=f"User {sample_user}: {sample_data}", inline=False)
    
    await ctx.send(embed=embed)
    
    # Also print to console
    print(f"\n🔍 DEBUG DATA DUMP:")
    print(f"Messages: {dict(analytics_data['messages'])}")
    print(f"Reactions Given: {dict(analytics_data['reactions_given'])}")
    print(f"Reactions Received: {dict(analytics_data['reactions_received'])}")

@bot.command(name='debug_reactions')
async def debug_reactions(ctx):
    """Test reaction tracking by adding a reaction to this message (Debug mode only)"""
    if not DEBUG_MODE:
        await ctx.send("❌ Debug commands are only available when DEBUG_MODE is enabled.")
        return
        
    msg = await ctx.send("🔍 **Debug Test**: React to this message to test reaction tracking!")
    await msg.add_reaction("👍")
    await msg.add_reaction("❤️")
    await msg.add_reaction("🎉")
    
    print(f"\n🔍 DEBUG: Test message sent with reactions. Message ID: {msg.id}")

@bot.command(name='debug_clear')
async def debug_clear(ctx):
    """Clear all analytics data (use with caution!) (Debug mode only)"""
    if not DEBUG_MODE:
        await ctx.send("❌ Debug commands are only available when DEBUG_MODE is enabled.")
        return
        
    analytics_data['messages'] = defaultdict(lambda: defaultdict(int))
    analytics_data['reactions_given'] = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    analytics_data['reactions_received'] = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    
    # Save the cleared data
    save_data(analytics_data)
    
    await ctx.send("🔍 **Debug**: All analytics data cleared!")
    print(f"\n🔍 DEBUG: Analytics data cleared by {ctx.author.name}")

def main():
    """Main function to run the Discord Analytics Bot"""
    print("🚀 DISCORD BOT STARTUP INITIATED", flush=True)
    print("📅 Startup Time: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'), flush=True)
    print("🐍 Python Version: " + sys.version, flush=True)
    print("📁 Working Directory: " + os.getcwd(), flush=True)
    print("="*60, flush=True)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv('.env-SecretDiscordBotToken-NotPublishToGithub')
        print("📁 Local .env file loaded successfully", flush=True)
    except Exception as e:
        print("📁 No local .env file found (normal for cloud deployment)", flush=True)
        print("   Details: " + str(e), flush=True)
    
    # Set DEBUG_MODE
    global DEBUG_MODE
    debug_env_value = os.getenv('DEBUG_MODE', 'NOT_SET')
    DEBUG_MODE = debug_env_value.lower() in ['true', '1', 'yes', 'on']
    
    print(f"🔧 DEBUG_MODE: {DEBUG_MODE}", flush=True)
    if DEBUG_MODE:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Get Discord token
    token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not token:
        print("❌ ERROR: DISCORD_BOT_TOKEN not found!", flush=True)
        print("Setup: Add token to .env-SecretDiscordBotToken-NotPublishToGithub", flush=True)
        print("Get token: https://discord.com/developers/applications", flush=True)
        return
    
    print("✅ DISCORD_BOT_TOKEN found and loaded", flush=True)
    print("🚀 Starting Discord Analytics Bot...", flush=True)
    
    if DEBUG_MODE:
        print("🔍 Debug mode: Enhanced logging enabled", flush=True)
        print("🔧 Additional debug commands: !debug_data, !debug_reactions, !debug_clear", flush=True)
    
    print("📊 The bot will track messages and reactions in real-time!", flush=True)
    print("💡 Use !stats_help to see available commands", flush=True)
    print("", flush=True)
    print("="*50, flush=True)
    print("🔄 ATTEMPTING DISCORD CONNECTION...", flush=True)
    
    try:
        # Import discord here to catch import errors
        import discord
        print("✅ Discord.py import successful", flush=True)
        print("📦 Discord.py version: " + discord.__version__, flush=True)
        
        # Try to start the bot
        print("🔗 Connecting to Discord...", flush=True)
        bot.run(token)
        
    except ImportError as e:
        print("❌ CRITICAL ERROR: Discord.py not installed: " + str(e), flush=True)
        print("🔧 Solution: Install discord.py", flush=True)
        print("   pip install discord.py", flush=True)
        
    except discord.LoginFailure as e:
        print("❌ CRITICAL ERROR: Discord login failed: " + str(e), flush=True)
        print("🔧 Solutions:", flush=True)
        print("- Check that your bot token is correct", flush=True)
        print("- Make sure the token hasn't expired", flush=True)
        print("- Verify the bot exists in Discord Developer Portal", flush=True)
        
    except discord.PrivilegedIntentsRequired as e:
        print("❌ CRITICAL ERROR: Privileged intents required: " + str(e), flush=True)
        print("🔧 Solution:", flush=True)
        print("1. Go to Discord Developer Portal", flush=True)
        print("2. Select your bot application", flush=True)
        print("3. Go to Bot section", flush=True)
        print("4. Enable 'Message Content Intent' and 'Server Members Intent'", flush=True)
        print("5. Save changes and restart the bot", flush=True)
        
    except Exception as e:
        print("❌ UNEXPECTED ERROR: " + str(e), flush=True)
        print("   Error type: " + type(e).__name__, flush=True)
        print("   Error details: " + str(e), flush=True)
        print("", flush=True)
        print("🔧 Common solutions:", flush=True)
        print("- Check that your bot token is correct", flush=True)
        print("- Ensure the bot has proper permissions", flush=True)
        print("- Make sure discord.py is installed: pip install discord.py", flush=True)
        print("- Enable privileged intents in Discord Developer Portal", flush=True)
        print("- Check internet connection", flush=True)
        
        # Print full traceback in debug mode
        if DEBUG_MODE:
            import traceback
            print("", flush=True)
            print("🔍 DEBUG: Full error traceback:", flush=True)
            traceback.print_exc()
    
    print("🛑 BOT EXECUTION COMPLETED", flush=True)

if __name__ == "__main__":
    main()
