import { Hono } from "hono";
import { HTTPException } from "hono/http-exception";
import { logger } from "hono/logger";
import {
  fetchAttitudes,
  fetchRecommendations,
  fetchTrendings,
  fetchWallpapers,
} from "./request";

const app = new Hono();

app.use(logger());

app.get("/", (c) => {
  return c.text("ok");
});

app.get("/recommendation", async (c) => {
  const userId = c.req.header("X-User-Id");

  const recommendedWallpaperIds = await fetchRecommendations(userId);

  const [wallpapers, attitudes] = await Promise.all([
    fetchWallpapers(recommendedWallpaperIds),
    fetchAttitudes(userId, recommendedWallpaperIds),
  ]);

  const result = recommendedWallpaperIds.map((id) => ({
    id,
    ...wallpapers.find((w) => w.id === id),
    attitude: attitudes.find((a) => a.wallpaperId === id)?.attitude ?? null,
  }));

  return c.json(result);
});

app.get("/trending", async (c) => {
  const userId = c.req.header("X-User-Id");

  const trendingWallpaperIds = await fetchTrendings();

  const [wallpapers, attitudes] = await Promise.all([
    fetchWallpapers(trendingWallpaperIds),
    fetchAttitudes(userId, trendingWallpaperIds),
  ]);

  const result = trendingWallpaperIds.map((id) => ({
    id,
    ...wallpapers.find((w) => w.id === id),
    attitude: attitudes.find((a) => a.wallpaperId === id)?.attitude ?? null,
  }));

  return c.json(result);
});

app.onError((error, c) => {
  if (error instanceof HTTPException) {
    return c.json({ error: error.message }, error.status);
  }

  console.error(error);
  return c.json({ error: "Server error" }, 500);
});

export default app;
