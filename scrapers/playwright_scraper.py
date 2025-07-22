import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import os
import time
import random
from typing import List, Dict, Any, Optional
import structlog

logger = structlog.get_logger()

DEFAULT_TIMEOUT = 45  # seconds
CONCURRENCY_LIMIT = 3
SCREENSHOT_DIR = "scrapers/screenshots"
USER_AGENTS = [
    # Add more UAs as needed
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
]

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

class PlaywrightScraper:
    def __init__(self, headless: bool = True, browser: str = "chromium", concurrency: int = CONCURRENCY_LIMIT, timeout: int = DEFAULT_TIMEOUT):
        self.headless = headless
        self.browser = browser
        self.concurrency = concurrency
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(concurrency)

    async def scrape_menu(self, url: str, capture_screenshot: bool = False) -> Dict[str, Any]:
        retries = 0
        start_time = time.time()
        while retries < 3:
            try:
                async with self.semaphore:
                    async with async_playwright() as p:
                        browser = getattr(p, self.browser)
                        context = await browser.launch(headless=self.headless)
                        page = await context.new_page()
                        ua = random.choice(USER_AGENTS)
                        await page.set_user_agent(ua)
                        await page.goto(url, timeout=self.timeout * 1000)
                        # Heuristic: find menu containers
                        menu_blocks = await self._find_menu_blocks(page)
                        menu_items = await self._extract_menu_items(menu_blocks)
                        screenshot_path = None
                        if capture_screenshot:
                            screenshot_path = os.path.join(SCREENSHOT_DIR, f"{int(time.time())}_{random.randint(1000,9999)}.png")
                            await page.screenshot(path=screenshot_path)
                        await context.close()
                        duration = time.time() - start_time
                        return {
                            "success": True,
                            "menu_items": menu_items,
                            "raw_text": "\n".join([item["text"] for item in menu_items]),
                            "screenshot": screenshot_path,
                            "duration": duration,
                            "retries": retries,
                            "source_url": url
                        }
            except PlaywrightTimeoutError:
                logger.warn("scraper.timeout", url=url)
                retries += 1
            except Exception as e:
                logger.error("scraper.error", error=str(e), url=url)
                retries += 1
            await asyncio.sleep(2 * retries)
        duration = time.time() - start_time
        return {
            "success": False,
            "error": f"Failed after {retries} retries.",
            "duration": duration,
            "retries": retries,
            "source_url": url
        }

    async def _find_menu_blocks(self, page) -> List[Any]:
        # Heuristic: look for divs/sections with menu-like keywords
        candidates = await page.query_selector_all("div,section,ul")
        menu_blocks = []
        for c in candidates:
            text = (await c.inner_text()).lower()
            if any(k in text for k in ["menu", "entree", "main", "starters", "appetizer", "salad", "bowl", "plate", "specials"]):
                if not any(skip in text for skip in ["disclaimer", "ad", "terms", "policy"]):
                    menu_blocks.append(c)
        return menu_blocks

    async def _extract_menu_items(self, menu_blocks) -> List[Dict[str, str]]:
        items = []
        for block in menu_blocks:
            try:
                text = await block.inner_text()
                # Simple split: each line is a potential item
                for line in text.split("\n"):
                    if len(line.strip()) > 10 and not any(skip in line.lower() for skip in ["disclaimer", "ad", "terms", "policy"]):
                        items.append({"text": line.strip()})
            except Exception:
                continue
        return items 