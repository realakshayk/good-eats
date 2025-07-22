from playwright.sync_api import sync_playwright
import logging
import time
from typing import Optional
import hashlib
import os
import json
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache file for menu scraping
CACHE_FILE = '.gcache_menu.json'
CACHE_DURATION = timedelta(hours=24)

def load_cache():
    """Load cached menu data."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
    return {}

def save_cache(cache_data):
    """Save menu data to cache."""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save cache: {e}")

def get_cache_key(url: str) -> str:
    """Generate cache key for URL."""
    return hashlib.md5(url.encode()).hexdigest()

def is_cache_valid(timestamp_str: str) -> bool:
    """Check if cached data is still valid."""
    try:
        timestamp = datetime.fromisoformat(timestamp_str)
        return datetime.now() - timestamp < CACHE_DURATION
    except Exception:
        return False

def scrape_menu_text(url: str) -> str:
    """
    Scrape all visible text content from a restaurant website using Playwright.
    
    Args:
        url: Restaurant website URL to scrape
        
    Returns:
        String containing all visible text content from the page
        
    Raises:
        Exception: If scraping fails or timeout occurs
    """
    
    # Check cache first
    cache = load_cache()
    cache_key = get_cache_key(url)
    
    if cache_key in cache:
        cached_data = cache[cache_key]
        if is_cache_valid(cached_data['timestamp']):
            logger.info(f"Using cached menu data for {url}")
            return cached_data['content']
        else:
            logger.info(f"Cache expired for {url}, scraping fresh data")
    
    try:
        with sync_playwright() as p:
            # Launch Chromium browser
            browser = p.chromium.launch(headless=True)
            
            # Create a new page
            page = browser.new_page()
            
            # Set timeout to 15 seconds
            page.set_default_timeout(15000)
            
            # Set user agent to avoid detection
            page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            logger.info(f"Navigating to: {url}")
            
            # Navigate to the URL
            try:
                page.goto(url)
            except Exception as e:
                logger.error(f"Failed to navigate to {url}: {str(e)}")
                browser.close()
                raise Exception(f"Failed to navigate to {url}: {str(e)}")
            
            # Wait for the page to load completely
            try:
                page.wait_for_load_state('networkidle')
            except Exception as e:
                logger.warning(f"Timeout waiting for page load at {url}: {str(e)}")
                # Continue anyway, the page might still be usable
            
            # Additional wait for dynamic content (some pages load content after initial load)
            time.sleep(2)
            
            # Get all visible text content
            # This gets text from all visible elements
            text_content = page.evaluate("""
                () => {
                    // Get all text content from the body
                    let text = document.body.innerText || document.body.textContent || '';
                    
                    // Clean up the text
                    text = text.replace(/\\s+/g, ' ').trim();
                    
                    return text;
                }
            """)
            
            # Alternative method: get text from specific elements that might contain menu items
            menu_text = page.evaluate("""
                () => {
                    // Common selectors for menu items
                    const selectors = [
                        '[class*="menu"]',
                        '[class*="dish"]',
                        '[class*="food"]',
                        '[class*="item"]',
                        'article',
                        '.item',
                        '.menu-item',
                        '.dish',
                        '.food-item',
                        'li',
                        '.list-item'
                    ];
                    
                    let menuText = '';
                    
                    // Try to find menu-specific content
                    for (const selector of selectors) {
                        const elements = document.querySelectorAll(selector);
                        for (const element of elements) {
                            const text = element.innerText || element.textContent || '';
                            if (text.trim().length > 10) { // Only include substantial text
                                menuText += text + '\\n';
                            }
                        }
                    }
                    
                    // If no menu-specific content found, return general text
                    if (!menuText.trim()) {
                        menuText = document.body.innerText || document.body.textContent || '';
                    }
                    
                    return menuText.trim();
                }
            """)
            
            # Use menu-specific text if available, otherwise use general text
            final_text = menu_text if menu_text.strip() else text_content
            
            # Clean up the text
            final_text = final_text.replace('\n\n', '\n').replace('\n\n\n', '\n').strip()
            
            logger.info(f"Successfully scraped {len(final_text)} characters from {url}")
            
            # Close browser
            browser.close()
            
            # Cache the result
            cache[cache_key] = {
                'content': final_text,
                'timestamp': datetime.now().isoformat()
            }
            save_cache(cache)
            logger.info(f"Cached menu data for {url}")
            
            return final_text
            
    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        raise Exception(f"Failed to scrape menu from {url}: {str(e)}")

def test_menu_scraper():
    """Test function to demonstrate usage."""
    # Test with a sample restaurant website
    test_url = "https://example.com"  # Replace with actual restaurant URL
    
    try:
        print(f"Scraping menu from: {test_url}")
        menu_text = scrape_menu_text(test_url)
        
        print("Scraped text:")
        print("-" * 50)
        print(menu_text[:500] + "..." if len(menu_text) > 500 else menu_text)
        print("-" * 50)
        print(f"Total characters: {len(menu_text)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_menu_scraper() 