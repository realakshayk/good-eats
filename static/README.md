# Good Eats Static Web Interface

This folder contains a modern, mobile-first single-page frontend for Good Eats.

## Features
- Mobile-first, responsive layout
- PWA-ready (add manifest/service worker for offline)
- Geolocation, goal selector, macro sliders, exclusions
- Results grid with meal cards
- Local/session storage for preferences and caching
- Fast, embeddable, iframe/widget-ready

## Developer Setup
- Uses Tailwind CSS via CDN
- Vanilla JS (see js/main.js)
- No build step required (for dev)
- For production, bundle/minify with Vite/Parcel if desired

## Usage
- Place in `static/` directory of your FastAPI app
- Access via `/static/index.html`
- Edit `js/main.js` and `css/styles.css` for customization

## Deployment
- Can be served as a static site or embedded as a widget
- Add manifest.json and service worker for full PWA support

## Assets
- Place icons/images in `static/assets/` 