import type { Wallpaper } from "@/types.ts";
import { sql } from "bun";

export async function persist(wallpapers: Wallpaper[]) {
  const dbWallpapers = wallpapers.map((w) => ({
    id: w.id,
    description: w.description,
    width: w.width,
    height: w.height,
    small_url: w.smallUrl,
    regular_url: w.regularUrl,
    raw_url: w.rawUrl,
    deduplication_key: w.deduplicationKey,
  }));

  const rows = await sql`
    with rows as (
      insert into wallpapers ${sql(dbWallpapers)}
      on conflict (deduplication_key) do nothing
      returning 1
    )
    select count(*) from rows`;
  return rows[0].count as number;
}
