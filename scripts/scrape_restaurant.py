import argparse
import asyncio
from scrapers.playwright_scraper import PlaywrightScraper
import json

parser = argparse.ArgumentParser(description="Scrape restaurant menu by URL.")
parser.add_argument('--url', required=True, help='Restaurant menu URL')
parser.add_argument('--screenshot', action='store_true', help='Capture screenshot')
args = parser.parse_args()

async def main():
    scraper = PlaywrightScraper()
    result = await scraper.scrape_menu(args.url, capture_screenshot=args.screenshot)
    print(json.dumps(result, indent=2))

asyncio.run(main()) 