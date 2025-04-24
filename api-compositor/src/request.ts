import { HTTPException } from "hono/http-exception";

export async function fetchRecommendations(userId: string | undefined) {
  const res = await fetch(
    `${Bun.env.RECOMMENDER_BASE_URL}/recommendation${userId ? `?user_id=${userId}` : ""}`,
  );

  if (!res.ok) {
    throw new HTTPException(502, {
      message: "Failed to retrieve recommendation for you",
    });
  }

  const json = (await res.json()) as {
    wallpaper_id: string;
    similarity: number;
  }[];

  return json.map((item) => item.wallpaper_id);
}

export async function fetchTrendings(limit = 5) {
  const res = await fetch(
    `${Bun.env.TRENDING_TRACKER_BASE_URL}/trending?limit=${limit}`,
  );

  if (!res.ok) {
    throw new HTTPException(502, {
      message: "Failed to retrieve trending wallpapers",
    });
  }

  const json = await res.json();

  return json as string[];
}

export async function fetchWallpapers(wallpaperIds: string[]) {
  const res = await fetch(
    `${Bun.env.WALLPAPER_MANAGER_BASE_URL}/internal/wallpapers`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ wallpaperIds }),
    },
  );

  if (!res.ok) {
    throw new HTTPException(502, { message: "Failed to retrieve wallpapers" });
  }

  const json = await res.json();

  return json as {
    id: string;
    description: string;
    width: number;
    height: number;
    smallUrl: string;
    regularUrl: string;
    rawUrl: string;
  }[];
}

export async function fetchAttitudes(
  userId: string | undefined,
  wallpaperIds: string[],
) {
  if (!userId) {
    return wallpaperIds.map((id) => ({
      wallpaperId: id,
      attitude: null,
    }));
  }

  const res = await fetch(
    `${Bun.env.INTERACTION_CONTROLLER_BASE_URL}/internal/${userId}/attitudes`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ wallpaperIds }),
    },
  );

  if (!res.ok) {
    throw new HTTPException(502, { message: "Failed to retrieve attitudes" });
  }

  const json = await res.json();

  return json as {
    wallpaperId: string;
    attitude: "liked" | "disliked" | null;
  }[];
}
