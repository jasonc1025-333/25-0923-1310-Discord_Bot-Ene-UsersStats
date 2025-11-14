#!/usr/bin/env python3
"""
Admin Report Generator for Discord Analytics Bot
Generates a comprehensive terminal report of all user statistics without running the Discord bot.
"""

import json
import os
from collections import defaultdict
from datetime import datetime

def load_analytics_data():
    """Load analytics data from JSON file"""
    data_file = '02-DiscordBot-Users_Stats-DataReport_Output.json'
    if not os.path.exists(data_file):
        print("❌ No analytics data found!")
        print(f"   Make sure '{data_file}' exists in the current directory.")
        print("   Run the Discord bot first to collect some data.")
        return None
    
    try:
        with open(data_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading analytics data: {e}")
        return None

def get_user_display_name(user_id, user_cache={}):
    """Get a display name for user ID (cached for performance)"""
    if user_id in user_cache:
        return user_cache[user_id]
    
    # For this admin report, we'll just use User ID since we don't have Discord API access
    # In a real implementation, you could maintain a user mapping file
    display_name = f"User-{user_id}"
    user_cache[user_id] = display_name
    return display_name

def generate_comprehensive_report():
    """Generate and print a comprehensive analytics report"""
    print("="*80)
    print("📊 DISCORD ANALYTICS - COMPREHENSIVE ADMIN REPORT")
    print("="*80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load data
    data = load_analytics_data()
    if not data:
        return
    
    # Collect all users and their total stats
    user_stats = {}
    all_channels = set()
    
    # Process messages
    for user_id, channels in data.get('messages', {}).items():
        if user_id not in user_stats:
            user_stats[user_id] = {
                'display_name': get_user_display_name(user_id),
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
    for user_id, channels in data.get('reactions_given', {}).items():
        if user_id not in user_stats:
            user_stats[user_id] = {
                'display_name': get_user_display_name(user_id),
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
    for user_id, channels in data.get('reactions_received', {}).items():
        if user_id not in user_stats:
            user_stats[user_id] = {
                'display_name': get_user_display_name(user_id),
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
    
    # Top Users by Category
    print("🏆 TOP 10 LEADERBOARDS")
    print("-" * 40)
    
    # Top by messages
    top_messages = sorted(user_stats.items(), key=lambda x: x[1]['total_messages'], reverse=True)[:10]
    print("\n💬 Top Message Senders:")
    for i, (user_id, stats) in enumerate(top_messages, 1):
        if stats['total_messages'] > 0:
            print(f"  {i:2d}. {stats['display_name']:<20} {stats['total_messages']:,} messages")
    
    # Top by reactions given
    top_reactions_given = sorted(user_stats.items(), key=lambda x: x[1]['total_reactions_given'], reverse=True)[:10]
    print("\n👍 Top Reaction Givers:")
    for i, (user_id, stats) in enumerate(top_reactions_given, 1):
        if stats['total_reactions_given'] > 0:
            print(f"  {i:2d}. {stats['display_name']:<20} {stats['total_reactions_given']:,} reactions given")
    
    # Top by reactions received
    top_reactions_received = sorted(user_stats.items(), key=lambda x: x[1]['total_reactions_received'], reverse=True)[:10]
    print("\n⭐ Top Reaction Receivers:")
    for i, (user_id, stats) in enumerate(top_reactions_received, 1):
        if stats['total_reactions_received'] > 0:
            print(f"  {i:2d}. {stats['display_name']:<20} {stats['total_reactions_received']:,} reactions received")
    
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

def main():
    """Main function"""
    print("🚀 Starting Discord Analytics Admin Report Generator...")
    print()
    
    try:
        generate_comprehensive_report()
    except KeyboardInterrupt:
        print("\n\n⚠️  Report generation interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error generating report: {e}")
    
    print("\n✅ Admin report script completed.")

if __name__ == "__main__":
    main()
