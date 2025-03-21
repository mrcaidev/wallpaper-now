import { type Context, Hono } from "hono";
import { HTTPException } from "hono/http-exception";
import { logger } from "hono/logger";
import { validator } from "hono/validator";

const app = new Hono();

app.use(logger());

app.get("/", (c) => {
  return c.text("ok");
});

const WEIGHTS = {
  like: 3,
  dislike: -3,
  download: 5,
} as const;

app.post(
  "/interactions",
  validator("json", (json) => {
    const { wallpaperId, action } = json;

    if (!wallpaperId || typeof wallpaperId !== "string") {
      throw new HTTPException(400, { message: "Wallpaper ID is required" });
    }

    const UUID_REGEXP =
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;
    if (!UUID_REGEXP.test(wallpaperId)) {
      throw new HTTPException(400, { message: "Wallpaper ID is invalid" });
    }

    if (!action || typeof action !== "string") {
      throw new HTTPException(400, { message: "Action is required" });
    }

    if (!(action in WEIGHTS)) {
      throw new HTTPException(400, { message: "Action is not supported" });
    }

    return { wallpaperId, action };
  }),
  async (c) => {
    const userId = c.req.header("X-User-Id");

    if (!userId) {
      throw new HTTPException(401, { message: "Please log in first" });
    }

    const { wallpaperId, action } = c.req.valid("json");

    console.log({ userId, wallpaperId, action });

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
