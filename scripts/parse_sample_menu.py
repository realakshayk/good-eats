import argparse
from parsers.openai_parser import OpenAIParser
import asyncio
import json

parser = argparse.ArgumentParser(description="Parse sample menu with OpenAI parser.")
parser.add_argument('--input', required=True, help='Menu text file or string')
args = parser.parse_args()

async def main():
    parser = OpenAIParser()
    if args.input.endswith('.txt'):
        with open(args.input, 'r') as f:
            menu = f.read()
    else:
        menu = args.input
    result = await parser.parse_menu(menu)
    print(json.dumps(result, indent=2))

asyncio.run(main()) 