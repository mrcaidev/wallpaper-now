# Wallpaper Manager

Scrapes wallpapers from Internet and manages them.

## Responsibilities

- Scrapes wallpapers from various external sources, such as Unsplash, WallpaperHub, etc.
- Provides an external API to scrape more wallpapers.
- Provides an interal API to retrieve information of multiple wallpapers.

## Events

### WallpaperScraped

A batch of wallpapers has been scraped.

```json
{
  "wallpapers": [
    {
      "id": "03c7d4d2-cc77-4882-9d76-ad32fbfa23bf",
      "description": "A wonderful wallpaper",
      "width": 3840,
      "height": 2160,
      "smallUrl": "https://example.com/1/small.jpg",
      "regularUrl": "https://example.com/1/regular.jpg",
      "rawUrl": "https://example.com/1/raw.jpg"
    },
    {
      "id": "72dda60f-29f2-4796-8ac9-5c600a6b5d41",
      "description": "Another nice wallpaper",
      "width": 1920,
      "height": 1080,
      "smallUrl": "https://example.com/2/small.jpg",
      "regularUrl": "https://example.com/2/regular.jpg",
      "rawUrl": "https://example.com/2/raw.jpg"
    }
  ]
}
```

- `wallpapers`: A list of newly scraped wallpapers. Contains at most 100 wallpapers; if there are more, the event will be sent multiple times.
  - `id`: Unique identifier of the wallpaper in UUID v4 format.
  - `description`: Description of the wallpaper.
  - `width`: Width of the wallpaper in pixels.
  - `height`: Height of the wallpaper in pixels.
  - `smallUrl`: URL of the small-sized wallpaper.
  - `regularUrl`: URL of the regular-sized wallpaper.
  - `rawUrl`: URL of the raw-sized wallpaper.
