# Wallpaper Now

A wallpaper discovery platform, powered by big data.

## Prerequisites

None.

## Build & Run

Start all services.

```sh
docker compose up -d --build
```

Scrape wallpapers in batches.

```sh
curl http://localhost/api/scrape --json '{"total":100}' -H 'Authorization: Bearer only-i-can-scrape-new-wallpapers'
```

> The number "100" above indicates the total number of wallpapers ingested in this batch. It can be replaced with any number between 1 and 2000.
>
> This API returns 204, so it's normal to not see any output.

Go to [http://localhost](http://localhost) to use the app.

When not logged in, recommendations are randomly selected, and interactions are disabled.

Log in to the platform by clicking on the "Log in" button in the top right corner. A new account will automatically be created for any newcomer.

After successful login, the user can interact with any wallpaper by liking / disliking / downloading it. Scroll down to see more recommended wallpapers.

## Directory Structure

- `api-compositor`: Microservice. Compose responses from multiple APIs.
- `init`: Helper scripts, used by Docker Compose. Initialize Kafka topics.
- `interaction-collector`: Microservice. Collect real-time user clickstreams.
- `nginx`: Simple gateway.
- `recommend`: Microservice. Content-based recommendation engine.
- `trending-analyzer`: Microservice. Track trending wallpapers.
- `user-manager`: Microservice. Simple user management.
- `wallpaper-manager`: Microservice. Scrape and store wallpapers.
- `wallpapper-processor`: Microservice. Vectorizes wallpapers.
- `web-app`: SPA frontend.
- `docker-compose.yml`: Entrypoint to start all services.

## Contact

[mrcaidev@gmail.com](mailto:mrcaidev@gmail.com)
