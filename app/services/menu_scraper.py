import asyncio
from playwright.async_api import async_playwright
from typing import List, Optional, Dict, Any
from app.models import Restaurant
from app.utils.config import settings
import logging
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class MenuScraperService:
    """Service for scraping restaurant menus using Playwright."""
    
    def __init__(self):
        self.timeout = settings.SCRAPING_TIMEOUT * 1000  # Convert to milliseconds
    
    async def scrape_menu(self, restaurant: Restaurant) -> List[Dict[str, Any]]:
        """
        Scrape menu items from a restaurant's website.
        
        Args:
            restaurant: Restaurant object with website URL
            
        Returns:
            List of menu items with name, description, and price
        """
        if not restaurant.website:
            logger.warning(f"No website available for {restaurant.name}")
            return []
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Set timeout and user agent
                page.set_default_timeout(self.timeout)
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                # Navigate to the website
                await page.goto(restaurant.website)
                
                # Wait for content to load
                await page.wait_for_load_state('networkidle')
                
                # Extract menu items using common selectors
                menu_items = await self._extract_menu_items(page)
                
                await browser.close()
                
                logger.info(f"Scraped {len(menu_items)} menu items from {restaurant.name}")
                return menu_items
                
        except Exception as e:
            logger.error(f"Error scraping menu for {restaurant.name}: {str(e)}")
            return []
    
    async def _extract_menu_items(self, page) -> List[Dict[str, Any]]:
        """
        Extract menu items from the page using various selectors.
        
        Args:
            page: Playwright page object
            
        Returns:
            List of menu items
        """
        menu_items = []
        
        # Common selectors for menu items
        selectors = [
            # Menu item containers
            '[class*="menu-item"]',
            '[class*="dish"]',
            '[class*="food-item"]',
            '[class*="item"]',
            # Generic containers
            'article',
            '.item',
            '.menu-item',
            '.dish',
            '.food-item',
            # List items
            'li',
            '.list-item'
        ]
        
        for selector in selectors:
            try:
                elements = await page.query_selector_all(selector)
                
                for element in elements:
                    try:
                        # Extract text content
                        text_content = await element.text_content()
                        if not text_content or len(text_content.strip()) < 10:
                            continue
                        
                        # Extract item details
                        item = await self._parse_menu_item(element, text_content)
                        if item and item['name']:
                            menu_items.append(item)
                            
                    except Exception as e:
                        logger.debug(f"Error parsing element: {str(e)}")
                        continue
                        
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {str(e)}")
                continue
        
        # Remove duplicates based on name
        unique_items = []
        seen_names = set()
        
        for item in menu_items:
            name = item['name'].lower().strip()
            if name not in seen_names and len(name) > 2:
                seen_names.add(name)
                unique_items.append(item)
        
        return unique_items[:50]  # Limit to 50 items
    
    async def _parse_menu_item(self, element, text_content: str) -> Optional[Dict[str, Any]]:
        """
        Parse a menu item element to extract name, description, and price.
        
        Args:
            element: Playwright element
            text_content: Text content of the element
            
        Returns:
            Dictionary with menu item details
        """
        try:
            # Clean and split text
            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            
            if len(lines) < 1:
                return None
            
            # Extract price using regex
            price_pattern = r'\$?\d+\.?\d*'
            price_match = re.search(price_pattern, text_content)
            price = price_match.group() if price_match else None
            
            # Remove price from text for name/description
            clean_text = re.sub(price_pattern, '', text_content).strip()
            
            # Split into name and description
            parts = clean_text.split('\n')
            name = parts[0].strip() if parts else ""
            description = '\n'.join(parts[1:]).strip() if len(parts) > 1 else None
            
            # Clean up name and description
            name = re.sub(r'[^\w\s\-&]', '', name).strip()
            if description:
                description = re.sub(r'[^\w\s\-&,.]', '', description).strip()
            
            if not name or len(name) < 2:
                return None
            
            return {
                'name': name,
                'description': description,
                'price': price
            }
            
        except Exception as e:
            logger.debug(f"Error parsing menu item: {str(e)}")
            return None
    
    async def scrape_multiple_menus(self, restaurants: List[Restaurant]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scrape menus from multiple restaurants concurrently.
        
        Args:
            restaurants: List of Restaurant objects
            
        Returns:
            Dictionary mapping restaurant place_id to menu items
        """
        tasks = []
        for restaurant in restaurants:
            if restaurant.website:
                task = self.scrape_menu(restaurant)
                tasks.append((restaurant.place_id, task))
        
        results = {}
        for place_id, task in tasks:
            try:
                menu_items = await task
                results[place_id] = menu_items
            except Exception as e:
                logger.error(f"Error scraping menu for restaurant {place_id}: {str(e)}")
                results[place_id] = []
        
        return results 