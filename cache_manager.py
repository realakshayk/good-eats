#!/usr/bin/env python3
"""
Cache management utility for Good Eats API.
"""

import os
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache files
CACHE_FILES = [
    '.gcache',  # SQLite cache for requests
    '.gcache_menu.json',  # Menu scraping cache
    '.gcache_openai.json'  # OpenAI responses cache
]

def list_cache_files():
    """List all cache files and their sizes."""
    print("Cache Files:")
    print("=" * 50)
    
    total_size = 0
    for cache_file in CACHE_FILES:
        if os.path.exists(cache_file):
            size = os.path.getsize(cache_file)
            total_size += size
            modified = datetime.fromtimestamp(os.path.getmtime(cache_file))
            print(f"✓ {cache_file}")
            print(f"  Size: {size:,} bytes")
            print(f"  Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"✗ {cache_file} (not found)")
        print()
    
    print(f"Total cache size: {total_size:,} bytes ({total_size / 1024:.1f} KB)")

def clear_cache():
    """Clear all cache files."""
    print("Clearing cache files...")
    
    cleared_count = 0
    for cache_file in CACHE_FILES:
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
                print(f"✓ Removed {cache_file}")
                cleared_count += 1
            except Exception as e:
                print(f"✗ Failed to remove {cache_file}: {e}")
        else:
            print(f"- {cache_file} (already not found)")
    
    print(f"\nCleared {cleared_count} cache files")

def show_cache_stats():
    """Show statistics about cached data."""
    print("Cache Statistics:")
    print("=" * 50)
    
    # Menu cache stats
    menu_cache_file = '.gcache_menu.json'
    if os.path.exists(menu_cache_file):
        try:
            with open(menu_cache_file, 'r', encoding='utf-8') as f:
                menu_cache = json.load(f)
            print(f"Menu cache entries: {len(menu_cache)}")
            
            # Show some sample URLs
            urls = list(menu_cache.keys())[:3]
            for url_hash in urls:
                entry = menu_cache[url_hash]
                timestamp = datetime.fromisoformat(entry['timestamp'])
                print(f"  - {url_hash[:8]}... (cached: {timestamp.strftime('%Y-%m-%d %H:%M')})")
        except Exception as e:
            print(f"Error reading menu cache: {e}")
    else:
        print("Menu cache: Not found")
    
    print()
    
    # OpenAI cache stats
    openai_cache_file = '.gcache_openai.json'
    if os.path.exists(openai_cache_file):
        try:
            with open(openai_cache_file, 'r', encoding='utf-8') as f:
                openai_cache = json.load(f)
            print(f"OpenAI cache entries: {len(openai_cache)}")
            
            # Show some sample goals
            goals = list(openai_cache.keys())[:3]
            for goal_hash in goals:
                entry = openai_cache[goal_hash]
                timestamp = datetime.fromisoformat(entry['timestamp'])
                print(f"  - {goal_hash[:8]}... (cached: {timestamp.strftime('%Y-%m-%d %H:%M')})")
        except Exception as e:
            print(f"Error reading OpenAI cache: {e}")
    else:
        print("OpenAI cache: Not found")

def main():
    """Main function."""
    import sys
    
    if len(sys.argv) < 2:
        print("Good Eats Cache Manager")
        print("=" * 30)
        print("Usage:")
        print("  python cache_manager.py list    - List cache files")
        print("  python cache_manager.py clear   - Clear all cache files")
        print("  python cache_manager.py stats   - Show cache statistics")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'list':
        list_cache_files()
    elif command == 'clear':
        clear_cache()
    elif command == 'stats':
        show_cache_stats()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: list, clear, stats")

if __name__ == "__main__":
    main() 