import { type Context, Hono } from "hono";
import { HTTPException } from "hono/http-exception";
import { logger } from "hono/logger";
import { validator } from "hono/validator";
import { sendWallpaperScrapedEvent } from "./kafka.ts";
import { scrape } from "./scraper/index.ts";

const app = new Hono();

app.use(logger());

app.get("/", (c) => {
  return c.text("ok");
});

app.post(
  "/scrape",
  validator("header", (header) => {
    if (header.authorization !== `Bearer ${Bun.env.API_KEY}`) {
      throw new HTTPException(401, { message: "Unauthorized" });
    }
  }),
  validator("json", (json) => {
    const total = Number(json.total);

    if (Number.isNaN(total) || !Number.isInteger(total)) {
      throw new HTTPException(400, { message: "Total should be an integer" });
    }

    if (total < 1 || total > 2000) {
      throw new HTTPException(400, {
        message: "Total should be between 1 and 2000",
      });
    }

    return { total };
  }),
  async (c) => {
    const { total } = c.req.valid("json");

    const wallpapers = await scrape(total);
    await sendWallpaperScrapedEvent(wallpapers);

    return c.body(null, 204);
  },
);

app.onError((error: unknown, c: Context) => {
  if (error instanceof HTTPException) {
    return c.json({ error: error.message }, error.status);
  }

  console.error(error);
  return c.json({ error: "Server error" }, 500);
});

export default app;
