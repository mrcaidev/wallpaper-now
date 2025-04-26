import { sql } from "bun";
import { type Context, Hono } from "hono";
import { HTTPException } from "hono/http-exception";
import { logger } from "hono/logger";
import { validator } from "hono/validator";
import { sendInteractionCollectedEvent } from "./kafka.ts";
import type { Interaction } from "./types.ts";
import { isUuid } from "./utils.ts";

const app = new Hono();

app.use(logger());

app.get("/", (c) => {
  return c.text("ok");
});

const WEIGHTS = {
  like: 0.2,
  dislike: -0.4,
  download: 0.4,
} as const;

app.post(
  "/interactions",
  validator("json", (json) => {
    const { wallpaperId, action } = json;

    if (typeof wallpaperId !== "string") {
      throw new HTTPException(400, {
        message: "Wallpaper ID should be a string",
      });
    }

    if (!isUuid(wallpaperId)) {
      throw new HTTPException(400, { message: "Wallpaper ID is invalid" });
    }

    if (typeof action !== "string") {
      throw new HTTPException(400, { message: "Action should be a string" });
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

    const oldRows = await sql`
      select
        user_id as "userId",
        wallpaper_id as "wallpaperId",
        liked_at as "likedAt",
        disliked_at as "dislikedAt",
        downloaded_at as "downloadedAt"
      from interactions
      where user_id = ${userId} and wallpaper_id = ${wallpaperId}`;
    const oldInteraction = oldRows[0] as Interaction | undefined;

    if (!oldInteraction) {
      await sql`
        insert into interactions (
          user_id,
          wallpaper_id,
          liked_at,
          disliked_at,
          downloaded_at
        )
        values (
          ${userId},
          ${wallpaperId},
          ${action === "like" ? new Date() : null},
          ${action === "dislike" ? new Date() : null},
          ${action === "download" ? new Date() : null}
        )
        returning
          user_id as "userId",
          wallpaper_id as "wallpaperId",
          liked_at as "likedAt",
          disliked_at as "dislikedAt",
          downloaded_at as "downloadedAt"`;
    } else {
      await sql`
        update interactions
        set
          liked_at = case
            when ${action} = 'like' then
            case when liked_at is null then now() else null end
            when ${action} = 'dislike' then null
            else liked_at
            end,
          disliked_at = case
            when ${action} = 'dislike' then
            case when disliked_at is null then now() else null end
            when ${action} = 'like' then null
            else disliked_at
            end,
          downloaded_at = case
            when ${action} = 'download' then now()
            else downloaded_at
            end
        where user_id = ${userId} and wallpaper_id = ${wallpaperId}
        returning
          user_id as "userId",
          wallpaper_id as "wallpaperId",
          liked_at as "likedAt",
          disliked_at as "dislikedAt",
          downloaded_at as "downloadedAt"`;
    }

    await sendInteractionCollectedEvent({
      userId,
      wallpaperId,
      weight: diffWeight(oldInteraction, action),
      collectedAt: new Date().toISOString(),
    });

    return c.body(null, 204);
  },
);

function diffWeight(oldInteraction: Interaction | undefined, action: string) {
  const { likedAt, dislikedAt, downloadedAt } = oldInteraction ?? {};
  const code = `${likedAt ? "1" : "0"}${dislikedAt ? "1" : "0"}${downloadedAt ? "1" : "0"}`;

  switch (action) {
    case "like": {
      switch (code) {
        case "000":
          return WEIGHTS.like;
        case "100":
          return -WEIGHTS.like;
        case "010":
          return -WEIGHTS.dislike + WEIGHTS.like;
        case "001":
        case "101":
          return 0;
        case "011":
          return -WEIGHTS.dislike + WEIGHTS.download;
        default:
          throw new HTTPException(400, {
            message: "State transition is not supported",
          });
      }
    }
    case "dislike": {
      switch (code) {
        case "000":
          return WEIGHTS.dislike;
        case "010":
          return -WEIGHTS.dislike;
        case "100":
          return -WEIGHTS.like + WEIGHTS.dislike;
        case "001":
        case "101":
          return -WEIGHTS.download + WEIGHTS.dislike;
        case "011":
          return -WEIGHTS.dislike + WEIGHTS.download;
        default:
          throw new HTTPException(400, {
            message: "State transition is not supported",
          });
      }
    }
    case "download": {
      switch (code) {
        case "001":
        case "011":
        case "101":
          return 0;
        case "000":
          return WEIGHTS.download;
        case "100":
          return WEIGHTS.download - WEIGHTS.like;
        case "010":
          return 0;
        default:
          throw new HTTPException(400, {
            message: "State transition is not supported",
          });
      }
    }
    default:
      throw new HTTPException(400, { message: "Action is not supported" });
  }
}

app.post(
  "/internal/:userId/attitudes",
  validator("param", (param) => {
    const { userId } = param;

    if (typeof userId !== "string") {
      throw new HTTPException(400, { message: "User ID should be a string" });
    }

    if (!isUuid(userId)) {
      throw new HTTPException(400, { message: "User ID is invalid" });
    }

    return { userId };
  }),
  validator("json", (json) => {
    const { wallpaperIds } = json;

    if (!Array.isArray(wallpaperIds)) {
      throw new HTTPException(400, {
        message: "Wallpaper IDs should be an array",
      });
    }

    if (wallpaperIds.some((id) => typeof id !== "string" || !isUuid(id))) {
      throw new HTTPException(400, {
        message: "Some wallpaper IDs are invalid",
      });
    }

    return { wallpaperIds };
  }),
  async (c) => {
    const { userId } = c.req.valid("param");
    const { wallpaperIds } = c.req.valid("json");

    if (wallpaperIds.length === 0) {
      return c.json([]);
    }

    const rows: Pick<Interaction, "wallpaperId" | "likedAt" | "dislikedAt">[] =
      await sql`
      select
        wallpaper_id as "wallpaperId",
        liked_at as "likedAt",
        disliked_at as "dislikedAt"
      from interactions
      where user_id = ${userId} and wallpaper_id in (${sql.unsafe(wallpaperIds.map((id) => `'${id}'`).join(","))})`;

    const attitudes: {
      wallpaperId: string;
      attitude: "liked" | "disliked" | null;
    }[] = [];
    for (const wallpaperId of wallpaperIds) {
      const row = rows.find((r) => r.wallpaperId === wallpaperId);
      attitudes.push({
        wallpaperId,
        attitude: row?.likedAt ? "liked" : row?.dislikedAt ? "disliked" : null,
      });
    }

    return c.json(attitudes);
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
