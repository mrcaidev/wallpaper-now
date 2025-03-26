# Wallpaper Now

A wallpaper discovery platform, powered by big data.

## How to Run

After cloning the repository, run in the project root directory:

```bash
docker compose up -d --build
```

Visit the web frontend at [http://localhost](http://localhost), and the Kafka dashboard at [http://localhost:9090](http://localhost:9090).

## Project Structure

Each top-level directory is a mciroservice. Refer to their own README.md for more information on their responsibilities and emitted events.
