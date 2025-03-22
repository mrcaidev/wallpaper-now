import { type Context, Hono } from "hono";
import { HTTPException } from "hono/http-exception";
import { logger } from "hono/logger";
import { validator } from "hono/validator";

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
    const size = Number(json.size);

    if (Number.isNaN(size) || !Number.isInteger(size)) {
      throw new HTTPException(400, { message: "Size should be an integer" });
    }

    if (size < 1 || size > 100) {
      throw new HTTPException(400, {
        message: "Size should be between 1 and 100",
      });
    }

    return { size };
  }),
  async (c) => {
    const { size } = c.req.valid("json");
    console.log(`About to scrape ${size} wallpapers`);
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
